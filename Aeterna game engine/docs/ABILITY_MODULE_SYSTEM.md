# AETERNA Game Engine – Ability Module System

Ez a dokumentum az AETERNA Game Engine ability / effect module rendszerének fő tervezési váza.

Nem teljes rules engine specifikáció.

Nem végleges kártyaképesség-adatmodell.

Nem teljes runtime package schema.

Nem kártyaaudit-dokumentum.

Feladata, hogy meghatározza, hogyan lehet a kártyaszövegekből, structured mezőkből és runtime package adatokból fokozatosan programozható, diagnosztizálható, tesztelhető ability / effect rendszert építeni.

Kapcsolódó fő dokumentumok:

- DECISION_MAP.md
- ARCHITECTURE.md
- CONTRACT_SPECIFICATION.md
- RUNTIME_PACKAGE_SPECIFICATION.md
- TECHNOLOGY_DECISIONS.md
- OPEN_QUESTIONS.md
- CHECKPOINTS.md
- PROTOTYPE_PLANS.md

---

## 1. Alapelv

Az AETERNA kártyaképességeit hosszú távon nem egyedi, kártyánként kézzel írt szabálykóddal kell futtatni.

A hosszú távú cél:

- minél több képesség structured adatokból;
- újrahasználható trigger, condition, target, cost és effect modulokból;
- engine support státusszal;
- diagnostics-szal;
- event loggal;
- tesztelhető execution plan alapján működjön.

Alapelv:

**A kártyaszöveg emberi szabályszöveg. A structured ability és az ability registry a programlogikai köztes réteg.**

---

## 2. Miért kell ability module rendszer?

A kártyajáték képességei hosszú távon túl összetettek ahhoz, hogy minden lap külön kóddal fusson.

A module rendszer célja:

- ismétlődő hatások újrahasználása;
- kártyák engine support státuszának mérése;
- AI és balanszteszt előkészítése;
- diagnostics és audit erősítése;
- card-local fallback csökkentése;
- Godot és Python közötti közös logikai szerkezet előkészítése;
- ability execution későbbi tesztelhetősége.

A rendszernek támogatnia kell az átmeneti állapotot is, mert nem minden kártya lesz azonnal teljesen modularizálható.

---

## 3. Átmeneti modell

A projekt jelenlegi állapotában nem reális minden képességet azonnal teljesen programozható modulokra bontani.

Ezért az átmeneti modell:

1. Egyszerű képességek modularizálása.
2. Gyakori hatások közös effect module-ba emelése.
3. Komplex kártyák részleges modularizálása.
4. Egyedi kártyák ideiglenes fallback státusza.
5. Minden fallback diagnostics-ban látható.
6. Fallback lista későbbi migrációra.
7. Engine support report mutatja, mely kártya mennyire futtatható.

Fontos:

**A fallback átmeneti eszköz, nem hosszú távú alapműködés.**

---

## 4. Fő ability pipeline

Az ability / effect feldolgozás hosszú távú elvi lánca:

1. Emberi kártyaszöveg.
2. Structured ability mezők.
3. LOOKUPS / canonical értékek.
4. Runtime package normalizálás.
5. Ability registry.
6. Engine support checker.
7. Execution plan.
8. Rules engine / ability executor.
9. Event log.
10. Diagnostics.
11. Snapshot frissítés.
12. AI / balance report később.

A jelenlegi projektfázisban még nem minden réteg működik.

Jelenleg elsősorban az ability registry, runtime package és diagnostics előkészítése a cél.

---

## 5. Ability registry szerepe

Az ability registry a runtime package része vagy ahhoz szorosan kapcsolódó fájl.

Feladata:

- abilityk azonosítása;
- source card kapcsolása;
- module_id-k megadása;
- support státusz jelzése;
- fallback szükségességének jelzése;
- diagnostics kapcsolása;
- Godot loader és Python builder közös ability-információja.

Lehetséges fájl:

- ability_registry.json

A registry nem feltétlenül tartalmaz teljes végrehajtási logikát MVP-ben.

MVP-ben elég lehet, ha jelzi:

- melyik kártyán milyen ability van;
- mely ability supported;
- melyik partial;
- melyik unsupported;
- melyik fallback_required;
- milyen diagnostics kapcsolódik hozzá.

---

## 6. Ability azonosítók

Minden ability kapjon stabil azonosítót.

Lehetséges ability azonosító mezők:

- ability_id
- source_card_id
- source_card_name_hu
- ability_index
- printed_text_ref
- structured_source_ref

Az ability_id lehet generált, de legyen determinisztikus.

Példa elvi azonosítás:

- CARD_ID + ability index
- CARD_ID + structured ability group
- CARD_ID + trigger/effect rövidített kód

Fontos:

Az ability_id ne függjön olyan mezőtől, amely gyakran változik véletlenszerűen.

---

## 7. Ability fő mezői

Egy ability lehetséges fő mezői:

- ability_id
- source_card_id
- ability_type
- timing
- trigger
- conditions
- cost
- targets
- choices
- effects
- duration
- limits
- replacement
- prevention
- execution_mode
- support_status
- diagnostics
- metadata

MVP-ben nem minden mező kötelező.

A mezők fokozatosan bővíthetők, ahogy a structured adat és engine támogatás fejlődik.

---

## 8. Ability type

Lehetséges ability_type értékek:

- keyword
- static
- triggered
- activated
- replacement
- prevention
- continuous
- one_shot
- reaction
- passive
- unknown

Az ability_type célja:

- engine support mérés;
- legal action kapcsolás;
- event window kapcsolás;
- AI döntés-előkészítés;
- diagnostics kategorizálás.

Nyitott kérdés:

- a keyword képességek külön keyword registryben legyenek-e, vagy ability module-ként.

---

## 9. Trigger modulok

A trigger modul határozza meg, mikor indulhat vagy mikor figyel egy ability.

Lehetséges trigger típusok:

- on_play
- on_enter_domain
- on_enter_horizon
- on_enter_zenith
- on_destroyed
- on_ward_broken
- on_attack_declared
- on_combat_damage_to_entity
- on_entity_destroyed_in_combat
- on_spell_played
- on_incantation_played
- on_ritual_played
- on_turn_start
- on_turn_end
- on_aura_spent
- on_card_drawn
- on_card_discarded
- on_reaction_window

A pontos trigger értékek LOOKUPS és szabályaudit után véglegesíthetők.

---

## 10. Trigger modell nyitott kérdései

Nyitott kérdések:

- milyen trigger értékek legyenek MVP-ben;
- mely triggerek automatikusak;
- mely triggerek opcionálisak;
- több trigger egy abilityn belül hogyan kapcsolódik;
- több ability azonos triggerre milyen sorrendben fut;
- trigger sorrendnél ki választ;
- kell-e trigger priority;
- trigger event log hogyan nézzen ki.

Ezeket az OPEN_QUESTIONS.md is nyilvántartja.

---

## 11. Condition modulok

A condition modul azt határozza meg, hogy egy ability csak bizonyos feltétel mellett működik-e.

Lehetséges condition típusok:

- has_damaged_own_entity
- has_broken_own_ward
- has_standing_own_ward_count_at_most
- controls_entity
- controls_clan_entity
- target_is_damaged
- target_is_enemy_entity
- target_is_own_entity
- has_card_in_void
- has_temporary_aura
- source_is_on_horizon
- source_is_on_zenith
- phase_is
- turn_player_is

A condition modulok célja:

- runtime validáció;
- legal action szűrés;
- effect execution ellenőrzés;
- AI értékelés;
- diagnostics.

---

## 12. Cost modulok

A cost modul az ability vagy action költségét írja le.

Lehetséges cost típusok:

- aura_cost
- temporary_aura_cost
- exhaust_source
- sacrifice_entity
- discard_card
- move_card_to_void
- break_own_ward
- lose_temporary_aura
- conditional_cost
- additional_cost

Fontos:

A költség nem azonos az effecttel.

A költséget validálni kell, mielőtt az effect végrehajtódik.

Nyitott kérdések:

- meddig legyen automatikus Aura-fizetés;
- mikor kell manual payment;
- több forrás esetén payment window kell-e;
- alternatív költségek mikor kerüljenek be.

---

## 13. Target modulok

A target modul azt határozza meg, milyen objektumokat választhat a játékos vagy engine.

Lehetséges target típusok:

- own_entity
- enemy_entity
- any_entity
- damaged_own_entity
- damaged_enemy_entity
- own_ward
- enemy_ward
- broken_own_ward
- own_aeternal
- enemy_aeternal
- card_in_hand
- card_in_deck
- card_in_void
- own_sigil
- enemy_sigil
- current
- plane

Fontos:

Az Aeternal targetek csak nagyon szigorú korlátozással létezhetnek.

Az Aeternal nem HP objektum, nem damage/heal célpont.

---

## 14. Targeting nyitott kérdései

Nyitott kérdések:

- Aeternal target érték bekerüljön-e MVP-be;
- own_aeternal és enemy_aeternal mikor lehet érvényes;
- Pecsét targeteknél kell-e linked_current;
- több target hogyan kapcsolódik több effecthez;
- célpont sorrend számít-e;
- invalid target esetén teljes vagy részleges feloldás legyen;
- target selection külön legal action legyen-e.

---

## 15. Effect modulok

Az effect modul írja le, mit csinál az ability.

Lehetséges támogatandó effect modulok:

- deal_damage_to_entity
- heal_entity
- draw_cards
- discard_cards
- move_card
- create_token
- grant_keyword
- remove_keyword
- modify_atk
- modify_hp
- exhaust_entity
- ready_entity
- ward_break
- ward_restore
- ward_break_prevent
- gain_temporary_aura
- lose_temporary_aura
- search_deck
- reveal_card
- counter_incantation
- counter_ritual
- prevent_damage
- replace_event
- trigger_additional_effect

MVP-ben ezek közül csak kevés szükséges.

---

## 16. Tiltott vagy kerülendő effect modellek

Az Aeternal / Pecsét régi HP-modelljéből származó effectek kerülendők vagy tiltandók.

Kerülendő effect fogalmak:

- damage_player
- player_damage
- damage_aeternal
- aeternal_damage
- heal_player
- heal_aeternal
- seal_damage
- ward_damage
- ward_hp_change
- seal_hp_change

Helyette támogatandó:

- ward_break
- ward_restore
- ward_break_prevent
- aeternal_unprotected
- direct_attack_victory
- player_defeated

Ha régi HP-modell aktív runtime effectként jelenik meg, az diagnostics problémát okozzon.

---

## 17. Entity damage és healing

Az Entitás-sebzés és Entitás-gyógyítás támogatandó alap effect.

Lehetséges modulok:

- deal_damage_to_entity
- heal_entity
- prevent_damage_to_entity
- modify_entity_damage
- destroy_entity_if_damage_threshold

Fontos:

A heal_entity csak Entitásra vonatkozik.

Nem használható Aeternalra.

Nem használható Pecsét HP-gyógyításra.

---

## 18. Ward effectek

A Pecsét hatásokat HP nélkül kell modellezni.

Támogatandó ward effectek:

- ward_break
- ward_restore
- ward_break_prevent
- check_standing_ward_count
- check_broken_ward_exists

Lehetséges kapcsolódó eventek:

- ward_broken
- ward_restored
- ward_break_prevented

Nyitott kérdések:

- combatból és effectből származó ward_break azonos event_type legyen-e;
- ward_restore action, effect vagy event modellje hogyan nézzen ki;
- linked_current szükséges-e minden Pecsét célpontnál.

---

## 19. Aeternal effectek

Az Aeternal speciális szabályi fogalom.

Rögzített irány:

- Az Aeternal maga a játékos.
- Nem HP objektum.
- Nem kaphat sebzést.
- Nem gyógyítható.

Lehetséges engine szintű fogalmak:

- aeternal_unprotected
- direct_attack_victory
- player_defeated

Aeternalra vonatkozó hatások csak explicit engedélyezett, nagyon szűk szabálykörben létezhetnek.

MVP-ben érdemes kerülni az Aeternal targetek aktív használatát, kivéve ha szabályi okból szükséges.

---

## 20. Duration modulok

A duration modul megadja, meddig tart egy hatás.

Lehetséges duration értékek:

- instant
- until_end_of_turn
- until_next_turn
- while_source_in_play
- while_condition_true
- permanent
- one_attack
- one_combat
- next_event_only
- until_replaced

Nyitott kérdések:

- mely duration értékek legyenek MVP-supported;
- continuous effectek mikor kerüljenek be;
- replacement / prevention duration hogyan működjön;
- Sík hatások duration modellje külön szabályt igényel-e.

---

## 21. Limit modulok

A limit modul korlátozza egy ability használatát.

Lehetséges limit típusok:

- once_per_turn
- once_per_game
- once_per_card
- once_per_source
- once_per_phase
- limited_by_trigger
- limited_by_payment
- limited_by_condition
- no_repeat_this_turn

Nyitott kérdések:

- limit állapot hol tárolódjon;
- snapshotban látszódjon-e;
- legal action listában hogyan jelenjen meg;
- event logban legyen-e limit failure event.

---

## 22. Replacement és prevention

Replacement és prevention különösen fontos reakciók és védelmi képességek esetén.

Lehetséges module típusok:

- prevent_damage
- prevent_ward_break
- replace_destroy
- replace_draw
- replace_discard
- counter_effect
- redirect_target
- modify_event

Fontos:

A prevention és replacement rendszer szorosan kapcsolódik az event loghoz és reaction window modellhez.

Nyitott kérdések:

- kell-e stack / chain;
- elég-e reaction queue;
- prevention és replacement ugyanabba a reaction rendszerbe tartozzon-e;
- replacement event hogyan jelenjen meg;
- partially_resolved mikor keletkezzen.

---

## 23. Keyword rendszer

A kulcsszavak a kártyaszövegben rövidített képességek.

Fontos felhasználói döntés:

A kulcsszó jelentését nem kell minden kártyán teljes szövegben kiírni.

Ezért az engine-nek később valahol tárolnia kell a kulcsszó definíciókat.

Lehetséges megoldások:

1. Keyword registry külön fájlban.
2. Ability registry részeként.
3. Rules specification részeként.
4. Runtime package lookupként.
5. Hibrid: rules spec + runtime registry.

Nyitott kérdés:

- keywordök ability module-ként vagy külön keyword registryként működjenek-e.

---

## 24. MVP keyword támogatás

Lehetséges MVP keyword jelöltek:

- Gyorsaság
- Oltalom
- Hasítás
- Légies
- Métely
- Harmonizálás
- Rezonancia
- Visszhang
- Riadó
- Kényszerítés

Nem biztos, hogy mindegyik MVP-supported legyen.

A támogatási sorrendet később keyword audit alapján kell eldönteni.

Kérdések:

- mely keyword statikus;
- mely keyword event window-t igényel;
- mely keyword combat logikát igényel;
- mely keyword reaction rendszert igényel;
- unsupported keyword aktív kártyán mikor blokkoljon.

---

## 25. Execution plan

Az execution plan az ability végrehajtásának előkészített gépi terve.

Lehetséges szerepe:

- structured ability értelmezése;
- effect sorrend rögzítése;
- target és condition kapcsolat rögzítése;
- optional branch jelzése;
- partial resolution szabály előkészítése;
- event log előkészítés;
- diagnostics előkészítés;
- Python és GDScript közötti összehasonlítás alapja.

Nyitott kérdések:

- runtime package tartalmazzon-e előre generált execution plant;
- vagy a motor futáskor építse;
- Python és GDScript ugyanazt a plan-t használja-e;
- execution plan debugolható legyen-e;
- hibás execution plan package build error vagy runtime error legyen-e.

---

## 26. Execution mode

Lehetséges execution_mode értékek:

- fully_modular
- partially_modular
- card_local_fallback
- manual_only
- unsupported
- not_checked

Ezek segítenek az engine support reportban.

Ajánlott értelmezés:

- fully_modular: a képesség modulokból futtatható.
- partially_modular: részben futtatható, de van kézi vagy hiányzó rész.
- card_local_fallback: külön kártyaspecifikus logikát igényel.
- manual_only: engine nem futtatja, emberi játékban értelmezhető.
- unsupported: jelenlegi engine nem támogatja.
- not_checked: még nincs kiértékelve.

---

## 27. Support status

Lehetséges support_status értékek:

- supported
- partial
- unsupported
- not_checked
- fallback_required
- manual_review_required

A support_status nem csak technikai, hanem workflow információ is.

Használati célok:

- Godot loader figyelmeztetés;
- Python builder diagnostics;
- AI-vs-AI előszűrés;
- deck validation;
- full package readiness;
- card audit priorizálás.

Nyitott kérdés:

- unsupported mikor blocking.

---

## 28. Card-local fallback

A card-local fallback azt jelenti, hogy egy kártya képessége nem általános modulokból, hanem külön egyedi logikával futna.

Ez átmenetileg hasznos lehet, de veszélyes hosszú távon.

Szabályok:

- fallback mindig legyen diagnostics-ban látható;
- fallback mindig legyen engine support reportban látható;
- fallback legyen migrációs jelölt;
- fallback ne legyen észrevétlen normál működés;
- fallback engedélyezése build mode függő lehet.

Nyitott kérdések:

- normál játékban engedjük-e;
- AI-vs-AI tesztben engedjük-e;
- Godot/GDScript runtime-ban engedjük-e;
- mikor váljon blocking errorrá.

---

## 29. Structured mezők szerepe

A structured mezők a kártyaszöveg gépi értelmezését segítik.

Lehetséges structured csoportok:

- trigger;
- condition;
- target;
- cost;
- effect;
- duration;
- limit;
- timing;
- zone;
- keyword;
- effect tag;
- target tag.

Nyitott kérdések:

- jelenlegi structured oszlopok elég részletesek-e;
- kell-e parameter mező;
- kell-e secondary target;
- kell-e secondary effect;
- többértékű mezők hogyan kapcsolódnak;
- mikor kell új oszlop.

---

## 30. Hatáscímkék szerepe

A Hatáscímkék jelenleg nem feltétlenül futtatható effect modulok.

Lehetséges szerepeik:

- auditcímke;
- keresési címke;
- balance elemzési címke;
- engine support előjelzés;
- későbbi effect module mapping;
- diagnostics kategória.

Fontos:

A túl általános hatáscímke nem elég végrehajtási logikához.

Nyitott kérdések:

- Hatáscímkék mikor válhatnak engine-supported effect module-lá;
- effect tag sorrend számít-e;
- effect tag alapján készüljön-e support report;
- effect tag és structured ability mező hogyan kapcsolódjon.

---

## 31. Diagnostics kapcsolat

Minden ability feldolgozás generálhat diagnostics bejegyzést.

Lehetséges diagnostics helyzetek:

- unknown trigger;
- unknown target;
- unsupported effect;
- dangerous legacy effect;
- missing parameter;
- ambiguous structured mapping;
- workflow-only value runtime mezőben;
- card-local fallback required;
- partial support;
- invalid Aeternal target;
- invalid Pecsét HP effect;
- unknown keyword;
- missing lookup value.

A diagnostics legyen strukturált, ne sima szöveges hibalista.

---

## 32. Event log kapcsolat

Az ability execution eventeket generálhat.

Példák:

- ability_triggered
- ability_resolved
- ability_cancelled
- ability_partially_resolved
- target_chosen
- damage_dealt_to_entity
- entity_healed
- ward_broken
- ward_restored
- ward_break_prevented
- card_drawn
- card_discarded
- keyword_granted
- token_created
- effect_prevented
- effect_replaced

Az event log később kulcsfontosságú lesz:

- UI animációhoz;
- játékosbarát magyarázathoz;
- AI elemzéshez;
- replayhez;
- balance reporthoz.

---

## 33. Legal action kapcsolat

Egyes abilityk legal actiont generálhatnak vagy legal actionként jelenhetnek meg.

Példák:

- activated ability;
- optional trigger;
- choose target;
- choose option;
- pay cost;
- pass reaction;
- choose replacement;
- choose prevention.

A legal action lista nem frontend találgatásból készül.

Az ability module rendszernek adatot kell adnia a legal action generáláshoz.

---

## 34. Action request kapcsolat

Ha a játékos vagy AI abilityhez kapcsolódó döntést hoz, az action request formában történik.

Példák:

- ability aktiválása;
- célpont kiválasztása;
- opció választása;
- payment választása;
- reaction pass;
- prevention elfogadása;
- replacement választása.

Az action request validálása a rules engine / ability executor feladata.

---

## 35. Snapshot kapcsolat

Az ability hatásai snapshot változásokat eredményezhetnek.

Példák:

- Entitás sebződik;
- Entitás gyógyul;
- Pecsét feltörik;
- Pecsét visszaáll;
- kártya zónát vált;
- token létrejön;
- keyword ideiglenesen megjelenik;
- pending döntés nyílik;
- játékos veszít.

A snapshot nem maga az ability végrehajtás, hanem a végrehajtás utáni nézőpontfüggő állapotkép.

---

## 36. Runtime package kapcsolat

Az ability module rendszer a runtime package-ben több helyen megjelenhet:

- cards.jsonl structured ability mezőiben;
- ability_registry.json fájlban;
- engine_support.json fájlban;
- diagnostics.json fájlban;
- lookups.json értékkészleteiben;
- aliases.json canonical mappingjeiben.

A runtime package build során az ability adatok legalább alap validációt kapjanak.

---

## 37. LOOKUPS kapcsolat

A structured ability mezők értékei LOOKUPS kontroll alatt legyenek.

LOOKUPS feladatok:

- canonical értékek;
- Label_HU megjelenítés;
- active / inactive státusz;
- legacy alias;
- workflow-only értékek;
- runtime-supported státusz;
- danger flag;
- audit_required jelzés.

Nyitott kérdés:

- LOOKUPS és ability registry között hol legyen a határ.

---

## 38. Build mode és support

Az ability support kezelése build mode függő lehet.

Lehetséges build mode-ok:

- sample
- development
- strict
- audit
- ai_test
- balance_test
- release_candidate

Példák:

- sample mode engedhet unsupported elemeket, ha nem futnak.
- development mode warninggal továbbmehet.
- strict mode unknown effectet blokkol.
- ai_test mode deckben lévő unsupported abilityt blokkolhat.
- release_candidate mode nem enged fallback_required aktív lapokat.

---

## 39. MVP ability module scope

Az első MVP ability module rendszer ne próbáljon mindent lefedni.

Javasolt MVP cél:

- ability registry betöltése;
- support_status megjelenítése;
- unsupported / partial / fallback diagnostics;
- néhány egyszerű effect module;
- card reference resolution;
- simple legal action kapcsolódás;
- event log stub;
- smoke test.

Lehetséges első effect module-ok:

- draw_cards
- deal_damage_to_entity
- heal_entity
- ward_restore
- ward_break_prevent
- grant_keyword_until_end_of_turn
- create_token_simple

Nem biztos, hogy mind egyszerre szükséges.

---

## 40. Nem cél az MVP-ben

Nem cél első körben:

- teljes kártyaképesség rendszer;
- minden keyword;
- minden trigger;
- teljes combat rendszer;
- teljes reaction stack;
- minden replacement/prevention;
- Síkok teljes folyamatos hatásrendszere;
- teljes AI értékelés;
- teljes balanszteszt;
- minden AETERNA kártya futtathatósága;
- card-local fallback véglegesítése.

---

## 41. Első implementációs irány

Az első biztonságos implementációs irány:

1. Ability registry pontosítása.
2. Engine support státuszok stabilizálása.
3. Diagnostics output javítása.
4. Egy-két egyszerű effect module kiválasztása.
5. Simple execution plan minta.
6. Event log stub.
7. Action request / response smoke kapcsolat.
8. Godot debug megjelenítés.
9. Python builder validáció.
10. Smoke test.

Ez még mindig nem teljes rules engine.

---

## 42. Python és GDScript szerepe az ability rendszerben

Nyitott technológiai kérdés, hogy az ability execution hosszú távon hol fusson.

Lehetséges modellek:

1. Python ability executor.
2. GDScript ability executor.
3. Python reference executor + GDScript runtime executor.
4. Python package builder előre generált execution plan-nel, GDScript végrehajtással.
5. Hibrid, comparison testtel.

Jelenlegi biztonságos irány:

- a data model és registry legyen technológiafüggetlen;
- a runtime package legyen közös;
- a diagnostics és event log contract legyen közös;
- csak ezután döntsünk végleges executor technológiáról.

---

## 43. Comparison test lehetősége

Ha később Python és GDScript is képes ability executionre, szükség lehet comparison tesztre.

Cél:

- ugyanaz a scenario;
- ugyanaz a runtime package;
- ugyanaz az action request;
- Python és GDScript output összevetése;
- event log összevetése;
- diagnostics összevetése;
- snapshot változás összevetése.

Ez segíthet eldönteni, melyik engine viselkedése a referencia.

---

## 44. Kártyaaudit kapcsolat

Az ability module rendszer nem helyettesíti a kártyaauditot.

Viszont segíthet priorizálni:

- unsupported abilityk;
- ambiguous structured mezők;
- veszélyes legacy effectek;
- Pecsét/Aeternal hibás célpontok;
- unknown trigger értékek;
- túl általános Hatáscímkék;
- fallback_required kártyák;
- partial support kártyák.

Az új teljes kártyaaudit csak későbbi fázisban induljon, stabilabb adatút és diagnostics után.

---

## 45. Balance kapcsolat

Az ability module rendszer később támogatja a balanszvizsgálatot.

Lehetséges balance adatok:

- milyen effectek gyakoriak;
- mely kártyák futnak túl gyakran;
- mennyi ward_break történik;
- mennyi draw/discard történik;
- mely abilityk okoznak gyors győzelmet;
- mely keywordök dominánsak;
- mely fallback képességek torzítják a tesztet.

Balance suspicion azonban nem runtime hiba.

Balance suspicion emberi döntést igénylő audit / elemzési jelzés.

---

## 46. Kiemelt Aeternal / Pecsét szabály

A rendszer minden ability feldolgozásnál védje a rögzített Aeternal / Pecsét szabálymodellt.

Rögzített irány:

- Aeternal nem HP objektum.
- Aeternal nem kaphat sebzést.
- Aeternal nem gyógyítható.
- Pecsét nem HP objektum.
- Pecsét feltörési / visszaállítási eseményként kezelendő.
- Ha nincs védelem, egy célba érő támadás azonnali vereség.

Ezért minden Aeternal/Pecsét hatást különösen szigorúan kell validálni.

---

## 47. Nyitott kérdések

A részletes nyitott kérdések központi helye:

- OPEN_QUESTIONS.md

Kiemelt ability témák:

- structured mezők részletessége;
- execution plan helye;
- card-local fallback szabályai;
- reaction rendszer;
- keyword MVP támogatás;
- Pecsét / Aeternal ability targetek;
- Hatáscímkék szerepe;
- ability registry és runtime package kapcsolata;
- engine support blocking szabályai;
- Python / GDScript executor kérdés.

---

## 48. Következő kapcsolódó dokumentumok

A következő kapcsolódó fájl:

- PROTOTYPE_PLANS.md

Ott kell kezelni:

- ability registry smoke test;
- simple effect executor prototype;
- action request smoke;
- runtime package + sample contracts integráció;
- card reference resolution;
- GDScript rules service minimál prototípus;
- Python / GDScript comparison scenario előkészítése.

---

## 49. Záró állapot

Az ability module rendszer jelenlegi döntési állapota:

- Szükséges hosszú távú réteg.
- Nem cél minden képesség azonnali teljes futtatása.
- Az ability registry és support_status az első fontos lépés.
- A card-local fallback átmeneti, látható, diagnosztizált megoldás lehet.
- A Pecsét / Aeternal HP-modell tiltása kiemelt validációs szabály.
- A végleges executor technológia még nyitott.
- A következő helyes lépés kis, ellenőrizhető ability/prototype lépésekből álljon.