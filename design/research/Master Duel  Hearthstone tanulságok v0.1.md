Rendben, ez a kitérő szerintem **nagyon jó helyen jön**, mert a Snapshot contract előtt pont azt kell tisztázni, hogy egy digitális kártyajátéknál **mit kell látnia a játékosnak, mit kell tudnia a motornak, és hogyan kell kezelni az akciókat / reakciókat / rejtett információt**.

## AETERNA — Master Duel / Hearthstone tanulságok v0.1

A két játék két eltérő mintát ad:

**Hearthstone** inkább egy gyors, digitálisra optimalizált CCG: a játék célja a tempós működés, ezért nincs klasszikus „minden akcióra ellenfél válaszolhat” reakciórendszer; a források szerint a játékot kifejezetten úgy tervezték, hogy az ellenfél körében ne legyenek kézi reakciók, a körök időzítettek, a játékos pedig a saját körében használja a manát lapokra és képességekre. ([Wikipedia][1])

**Yu-Gi-Oh! Master Duel** ezzel szemben sokkal inkább egy fizikai TCG-szabályrendszer digitális szimulátora. A Master Duel a Yu-Gi-Oh! TCG digitális változata, Solo és multiplayer módokkal, és a játék nyilvános leírásai szerint a fizikai TCG logikáját szimulálja, bár saját tiltó/korlátozó listával és kártyakiadási ütemmel. ([Wikipedia][2])

A két irány közül az AETERNA szempontjából **Master Duel közelebb áll a fizikai-TCG-elsődleges gondolkodáshoz**, míg Hearthstone sok jó ötletet adhat **UI-egyszerűsítésre, tempóra, automatikus triggerkezelésre és digitális felhasználói élményre**.

---

# 1. Legfontosabb tanulság: ne a UI legyen a szabálymotor

Mindkét játék alapján erősödik az a döntésünk, hogy az AETERNA-nál a szabálymotor legyen külön a vizuális rétegtől.

A Godot/GDScript irány emiatt továbbra is jó jelölt, de a szabálylogikát akkor sem szabad szétszórni UI-node-okba. A GDScript Python-szerű, de Godotra optimalizált saját nyelv; Godot több nyelvet támogat, köztük GDScriptet, C#-ot és C++-t, a GDScript pedig kifejezetten Godot scene-alapú architektúrájához van igazítva. ([Wikipedia][3])

**AETERNA-tanulság:**

A Snapshot contractban külön kell választani:

* belső match state;
* játékosnak látható snapshot;
* ellenfélnek látható snapshot;
* AI/debug snapshot;
* UI-megjelenítés.

A Godot frontend csak megjelenít és action requestet küld. A szabálymotor dönti el, hogy az action érvényes-e.

---

# 2. Hearthstone tanulság: tempó és egyszerűség

Hearthstone egyik legerősebb digitális tanulsága, hogy a játék gyorsaságát úgy éri el, hogy az ellenfél a másik játékos körében nem kap folyamatos kézi reakcióablakokat; a reaktív hatások nagyrészt automatikusan, a motor által kezelt triggerként működnek. A források szerint Hearthstone manarendszerrel dolgozik, a játékosok saját körükben játszanak ki lapokat, és a játékot a gyorsabb tempó érdekében úgy tervezték, hogy ne legyen kézi reakció minden ellenfél-akcióra. ([Wikipedia][1])

**AETERNA-ra fordítva:**

Ez nem azt jelenti, hogy nekünk is ki kell venni a reakciókat. Az AETERNA-ban vannak Jelek, Burst, triggerelt hatások, Pecsét-feltöréshez kötött események, tehát kell reakció- és eseményrendszer.

De Hearthstone alapján fontos kérdés:

> Minden lehetséges reakciónál meg kell-e állítani a játékot, vagy csak akkor, ha a játékosnak tényleges választása van?

Ez a Snapshot és Legal action contract szempontjából nagyon fontos.

Javasolt AETERNA-elv:

* automatikus kötelező hatások: a motor oldja fel;
* opcionális hatások: csak akkor kérjen döntést, ha tényleg van választás;
* reakcióablak: csak akkor jelenjen meg, ha van legalább egy valódi legal reaction;
* ismétlődő „nincs válaszom” ablakokat kerülni kell.

---

# 3. Master Duel tanulság: Chain / reakcióablak / fordított feloldás

Yu-Gi-Oh! legfontosabb programozási tanulsága a chain-rendszer. A Yu-Gi-Oh! szabályleírás szerint a chain egymásra válaszoló hatások sorozata, ahol a játékosok váltva reagálhatnak, majd a chain fordított sorrendben oldódik fel. ([Wikipedia][4])

AETHERNA-ban nem biztos, hogy ilyen összetett chain-rendszer kell, de a gondolat nagyon hasznos:

* kell egy **pending reaction window**;
* kell egy **response stack / effect stack** vagy egyszerűbb „reaction queue”;
* kell tudni, hogy ki válaszolhat;
* kell tudni, mikor zárul le az ablak;
* kell tudni, milyen sorrendben oldódnak fel a hatások;
* kell event log, hogy a játékos értse, mi történt.

**AETERNA-ra javasolt egyszerűsített modell:**

Nem kell teljes Yu-Gi-Oh!-szintű chain, de kell:

```text
trigger_event
→ collect_mandatory_effects
→ offer_optional_reactions
→ build_resolution_queue
→ resolve_effects
→ emit_events
→ update_snapshot
```

Ez különösen fontos lesz:

* Jel aktiválásnál;
* Burst Igéknél;
* Pecsét-feltörés megelőzésénél;
* sebzésmegelőzésnél;
* „amikor megsemmisül” típusú Visszhang-hatásoknál;
* replacement / prevention hatásoknál.

---

# 4. Master Duel tanulság: a fizikai szabályhűség ára a bonyolult UI

Master Duel erős példa arra, hogy ha egy digitális játék közel akar maradni a fizikai TCG komplexitásához, akkor sok válaszablakot, szabályellenőrzést és logot kell kezelnie. A nyilvános beszámolók szerint a Master Duel nagy erőssége, hogy a fizikai Yu-Gi-Oh! komplex szabályrendszerét digitálisan szimulálja, de új játékosoknak nehéz lehet követni, mi történik a hosszú kombók és gyors hatásláncok miatt. ([Diario AS][5])

**AETERNA-tanulság:**

Az AETERNA fizikai TCG marad, de a digitális játékban nem szabad olyan UI-t csinálni, ahol a játékos elveszik.

Ezért kell:

* világos event log;
* kiemelt „miért történt?” információ;
* egyszerű triggerüzenetek;
* jó célpontkiemelés;
* opcionális részletes debug log;
* kezdőbarát magyarázó mód;
* AI-vs-AI logban emberileg olvasható összefoglaló.

Snapshot contractba ez így kerülhet be:

```text
last_action_summary
pending_reason
visible_events
debug_events
explainable_effects
```

---

# 5. Rejtett információ kezelése

Mindkét játék tanulsága, hogy a snapshot nem lehet egyszerűen „minden játékállapot mindenkinek”.

A Hearthstone-ban vannak kézben lévő lapok, pakli, titkos/rejtett információk, és a játék digitális rendszere kezeli, mit láthat az ellenfél. A Yu-Gi-Oh!/Master Duel esetében pedig különösen fontosak a face-down lapok, Jelek/Csapdák, chainelhető válaszok és publikus/privát információk. A Yu-Gi-Oh! szabályrendszerben a pálya zónái, face-down lapok és deck/graveyard jellegű állapotok mind részei a játéknak. ([Wikipedia][4])

**AETERNA Snapshot contract tanulság:**

Kell legalább négy nézet:

1. `debug_snapshot`
2. `player_visible_snapshot`
3. `opponent_visible_snapshot`
4. `public_spectator_snapshot`

A Pecsét, Jel, kéz, pakli, Ősforrás és face-down / rejtett hatások miatt ez nagyon fontos.

Példa:

```text
card_ref:
  card_id
  card_instance_id
  visibility
  known_to
  face_down
  revealed
  owner_id
  controller_id
```

---

# 6. Legal action tanulságok

A jelenlegi AETERNA backend contract már ismer minimális actionöket: `end_turn`, `play_entity`, `play_trap`, de a saját dokumentált contract is jelzi, hogy még nincs spell execution, targeting execution, combat action execution vagy teljes trap activation.

Hearthstone alapján az action rendszer lehet gyors és aktív-játékos-központú.

Master Duel alapján viszont kell reakcióképes rendszer is.

**AETERNA javasolt köztes megoldás:**

A legal action lista ne csak ezt mondja:

```text
mit tehet az aktív játékos?
```

hanem ezt:

```text
ki dönt most?
milyen ablakban vagyunk?
miért kell dönteni?
milyen actionök választhatók?
kötelező-e választani?
lehet-e passzolni?
```

Új mezők a Legal action contracthoz:

```text
decision_context
window_type
priority_player
can_pass
is_reaction
is_optional
prompt_reason
```

Példa:

```text
window_type: ward_break_prevention
priority_player: player_1
prompt_reason: enemy effect would break own ward
legal_actions:
  - activate_sigil
  - pass_priority
```

---

# 7. Event log / Duel log tanulság

Master Duel kapcsán különösen fontos, hogy egy komplex TCG digitális változatában a játékosnak tudnia kell, mi történt. A beszámolók szerint még duel log mellett is előfordulhat, hogy nehéz követni az ellenfél hosszú kombóit, ha a játékos nem ismeri mélyen a rendszert. ([Diario AS][5])

**AETERNA-ban ezért nem elég egy technikai log.**

Kell legalább három logszint:

1. **Frontend event log**
   Mit animáljon / jelenítsen meg a Godot?

2. **Player explanation log**
   Emberileg: „Az ellenfél Igéje feltörte volna a Pecsétedet, de a Pecsétvédő Csapda megakadályozta.”

3. **Debug / audit log**
   Fejlesztői részlet: trigger, target, condition, effect module, status, warning.

Snapshot contractba érdemes betenni:

```text
recent_events
visible_event_log
explanation_log
debug_event_index
```

---

# 8. Collection / crafting / booster tanulság

Mindkét játék erős digitális collection-rendszerrel dolgozik. Hearthstone-ban a játékosok kártyacsomagokból és craftingból szerezhetnek kártyákat; a források szerint a kártyák csomagokból vagy arcane dusttal craftolva szerezhetők. ([Wikipedia][1]) Master Duelben is van gyűjtemény, pakliépítés, csomagok és kártyakészítés / lebontás jellegű rendszer a nyilvános leírások alapján. ([Wikipédia][6])

**AETERNA-tanulság:**

Ezt nem most kell implementálni, de a contractban és adatmodellben nem szabad kizárni.

Később külön réteg legyen:

```text
collection
owned_cards
crafting_currency
booster_products
deckbuilder
cosmetics
progression
```

De ez ne keveredjen össze a fizikai TCG-szabálymotorral.

---

# 9. Formátumok / banlist / legalitás tanulság

Hearthstone a Standard/Wild/Twist jellegű formátumokkal kezeli, hogy mely kártyák használhatók; a források szerint Standard az utóbbi időszak készleteire korlátoz, míg Wild szélesebb kártyakészletet enged. ([Wikipedia][1]) Master Duelnek saját Forbidden/Limited listája és kártyakiadási üteme van, ami eltérhet a fizikai TCG/OCG listáktól. ([Wikipedia][2])

**AETERNA-tanulság:**

Már most érdemes beépíteni a contract gondolkodásba:

```text
format_id
ruleset_version
card_pool_id
ban_status
play_legal_status
deck_validation_rules
```

Ez segíteni fog:

* alapjáték;
* kiegészítő;
* tesztpaklik;
* starter paklik;
* későbbi event formátumok;
* digitális-only tesztformátumok;
* fizikai hivatalos formátumok elkülönítésében.

---

# 10. Solo / tutorial tanulság

Master Duel Solo Mode-ja AI ellen játszható mód, amely történeteket / archetípusokat mutat be; a nyilvános leírások szerint a Solo Mode kártyatörténetek köré épülő AI elleni játékmód. ([Wikipedia][2]) Hearthstone solo adventure és más módjai szintén használtak külön kihívásokat és bossokat a játékmechanikák tanítására; a források szerint a solo challenge-ek segíthetnek erősebb pakliarchetípusok és stratégiák megértésében. ([Wikipedia][1])

**AETERNA-tanulság:**

Később nagyon hasznos lehet:

* Birodalom-tutorial;
* Klán-tutorial;
* mechanika-tutorial;
* teszt-scenario;
* puzzle-szerű helyzet;
* AI elleni tanítómeccs.

Ez a programnak is jó, mert ugyanaz a rendszer használható:

```text
test_scenario
tutorial_scenario
solo_challenge
ai_vs_ai_regression_test
```

A Snapshot contractban emiatt kellhet:

```text
scenario_id
objective
tutorial_hint
expected_action
```

---

# 11. A legfontosabb AETERNA-döntés ebből

Szerintem a két játék vizsgálata alapján az AETERNA-nak nem kell egy az egyben egyik irányt sem másolnia.

A helyes cél inkább:

## Master Duelből átvenni:

* fizikai TCG-szabályhűség igényét;
* reakcióablakok / chain-szerű gondolkodást;
* publikus és rejtett információ kezelését;
* duel log / event history fontosságát;
* formátum- és legalitáskezelést;
* AI/Solo mód hasznosságát.

## Hearthstone-ból átvenni:

* tempós UI-gondolkodást;
* automatikus triggerek kényelmét;
* egyszerű legal action élményt;
* játékosbarát board snapshotot;
* collection / crafting / pack rendszer későbbi rétegét;
* kezdőbarátabb digitális működés igényét.

## Amit kerülni kell:

* Master Duel-szerű túlzott prompt- és reakcióablak-terhelés;
* Hearthstone-szerű túlzott digital-only mechanika, ha fizikai TCG-ben nehezen kezelhető;
* UI-ba beégetett szabálylogika;
* átláthatatlan event log;
* két motor eltérése közös contract nélkül.

---

# 12. Konkrét módosítás a következő Snapshot contracthoz

A Snapshot contract v0.1-be ezek a tanulságok kerüljenek be:

```text
snapshot_type
viewer_id
visibility_mode
active_player
priority_player
phase
window_type
pending_action
pending_choices
legal_action_summary
reaction_stack_or_queue
recent_events
visible_event_log
explanation_log
hidden_information_policy
scenario_context
diagnostics_summary
```

És külön kell kezelni:

```text
debug_snapshot
player_visible_snapshot
opponent_visible_snapshot
spectator_snapshot
ai_test_snapshot
```

Ez lesz a legfontosabb változás ahhoz képest, mintha csak egy egyszerű „aktuális board állapot” snapshotot írnánk.

---

# 13. Előzetes ajánlás

A Snapshot contract előtt ez a kitérő szerintem ezt a döntést erősíti:

> Az AETERNA snapshot ne csak állapotkép legyen, hanem döntési és magyarázati állapot is.

Vagyis ne csak azt tartalmazza, hogy „mi van a pályán”, hanem azt is:

* ki dönt most;
* miért dönt;
* milyen ablakban vagyunk;
* mire lehet reagálni;
* mit lát a játékos;
* mit nem lát;
* milyen események vezettek ide;
* van-e engine warning vagy audit note.

Ez Master Duel és Hearthstone tanulságait is jól beépíti, miközben az AETERNA saját célját tartja meg.

A következő lépés így továbbra is lehet a **Snapshot contract v0.1**, de már ezzel a kibővített szemlélettel.

[1]: https://en.wikipedia.org/wiki/Hearthstone?utm_source=chatgpt.com "Hearthstone"
[2]: https://en.wikipedia.org/wiki/Yu-Gi-Oh%21_Master_Duel?utm_source=chatgpt.com "Yu-Gi-Oh! Master Duel"
[3]: https://en.wikipedia.org/wiki/Godot_%28game_engine%29?utm_source=chatgpt.com "Godot (game engine)"
[4]: https://en.wikipedia.org/wiki/Yu-Gi-Oh%21_Trading_Card_Game?utm_source=chatgpt.com "Yu-Gi-Oh! Trading Card Game"
[5]: https://as.com/meristation/2022/01/24/analisis/1643032768_819214.html?utm_source=chatgpt.com "Yu-Gi-Oh! Master Duel, análisis - El simulador de Duelos definitivo"
[6]: https://fr.wikipedia.org/wiki/Yu-Gi-Oh%21_Master_Duel?utm_source=chatgpt.com "Yu-Gi-Oh! Master Duel"
