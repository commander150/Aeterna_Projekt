# AETERNA – Card-Forge/forge ELEMZÉS

## VERZIÓ / DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 0.1
- **Dátum:** 2026-08-15
- **Státusz:** célzott rules-engine source audit
- **Javasolt repository-útvonal:** `learning/analyses/card-forge__forge.md`
- **Repository:** `Card-Forge/forge`
- **Vizsgált branch:** `master`
- **Vizsgált commit:** `0aa78d4ff2333134297c1c19adb74d99ec18ca24`
- **Commit dátuma:** 2026-08-14
- **Fő technológia:** Java / Maven, többmodulos alkalmazás
- **Licenc:** repository `LICENSE` = GNU GPL v3; a vizsgált source-fejlécek GPL v3 vagy újabb formulát használnak
- **Elsődleges AETERNA-érték:** nagy TCG rules-engine trigger-, stack-, replacement/prevention- és simultaneous-ordering életciklus
- **Vizsgálati korlát:** build, teljes tesztfuttatás, teljes repository-audit és UI/network audit ebben a körben nem történt
- **Nem AETERNA-szabályforrás és nem engedély külső kód átvételére.**

---

# 1. Vizsgálati cél

A cél annak tisztázása volt, hogy egy nagy, hosszú életű TCG rules-engine hogyan választja szét:

- esemény létrejöttét;
- trigger felismerést;
- delayed/waiting trigger kezelést;
- simultaneous trigger orderinget;
- stackre helyezést;
- LIFO resolutiont;
- target revalidationt;
- replacement/prevention interceptiont.

A vizsgálat kizárólag az AETERNA jelenlegi C# authoritative engine és Reaction/Priority tervezési igényeihez viszonyít.

---

# 2. Vizsgált fő source-ok

| Terület | Fájl |
|---|---|
| trigger lifecycle | `forge-game/src/main/java/forge/game/trigger/TriggerHandler.java` |
| stack / resolution | `forge-game/src/main/java/forge/game/zone/MagicStack.java` |
| replacement / prevention | `forge-game/src/main/java/forge/game/replacement/ReplacementHandler.java` |
| replacement type | `forge-game/src/main/java/forge/game/replacement/ReplacementEffect.java` |
| game state/runtime | `forge-game/src/main/java/forge/game/` |

---

# 3. Trigger lifecycle

A `TriggerHandler` külön állományokban tart:

- aktív triggereket;
- delayed triggereket;
- current-turn delayed triggereket;
- player-defined delayed triggereket;
- `waitingTriggers` állományt.

A trigger létrejötte nem jelenti automatikusan azonnali feloldást.

Ha a stack fagyasztott vagy a hívó kifejezetten tartani akarja a triggert, a megfelelő trigger esemény `TriggerWaiting` formában félretehető. Később a `runWaitingTriggers()` dolgozza fel.

A trigger futtathatósága több külön ellenőrzésből áll:

- trigger mode;
- suppression;
- activation limit;
- általános requirement;
- triggering-object requirement;
- egyedi test;
- state-trigger duplikáció elkerülése;
- static ability által történő trigger-disable.

Ez AETERNA számára azt erősíti meg, hogy:

```text
event happened
≠
trigger is eligible
≠
trigger became pending
≠
trigger is ordered
≠
trigger resolves
```

Ezek külön lifecycle-lépések.

---

# 4. Optional és mandatory trigger

A triggerből létrejövő ability külön kezeli:

- mandatory esetet;
- optional decider esetet;
- cost miatt opcionálissá váló esetet.

A triggerből wrapper ability jön létre, és a nem-static trigger a simultaneous stack-entry gyűjteménybe kerül.

AETERNA-következtetés:

A kötelező/opcionális jellegnek trigger-payload/state adatnak kell lennie; nem UI-oldali döntésként kell utólag kitalálni.

---

# 5. Simultaneous trigger ordering

A `MagicStack` külön:

- `simultaneousStackEntryList`;
- `activePlayerSAs`;
- tényleges LIFO stack

állapotot tart.

Az egyszerre létrejövő abilityk nem közvetlenül kerülnek a stackre.

A rendszer:

1. összegyűjti őket;
2. meghatározza a játékossorrendet;
3. játékosonként kiválasztja az adott playerhez tartozó abilityket;
4. a játékos controllerével sorrendezteti őket;
5. csak ezután kerülnek a tényleges stackre.

A konkrét ordering szabály Magic-specifikus, ezért AETERNA számára nem másolandó.

Az általános minta viszont fontos:

> simultaneous detection és resolution order két külön lépés.

---

# 6. Stack és resolution

A `MagicStack` valódi LIFO tárolót használ.

Külön állapot létezik:

- normál stack;
- frozen stack;
- simultaneous pending entryk;
- undo stack;
- resolving flag;
- aktuálisan feloldódó forrás.

A stack fagyasztható egy összetett művelet közben. Unfreeze után:

- frozen abilityk kerülnek vissza;
- aktív triggerlista frissül;
- waiting triggereket feldolgozza.

Ez arra mutat, hogy a stabil resolution boundary explicit kezelése értékes.

---

# 7. Resolution-time revalidation

A stackelem feloldása előtt a rendszer újraellenőrzi a targetinget.

A `hasFizzled` logika:

- a korábban választott célokat újra megkeresi;
- object/state identity változást figyelembe vesz;
- újrafuttatja a `canTarget` ellenőrzést;
- illegális célokat eltávolít;
- a szabály által engedett esetben részleges resolution folytatódhat;
- ha semmi érvényes nem marad, a feloldás szabály szerint meghiúsulhat.

Az AETERNA hivatalos reaction szabálya szintén resolution előtti revalidationt igényel.

**AETERNA-candidate:** a reaction/ability resolution pipeline kötelezően külön `revalidate` lépést kapjon.

---

# 8. Replacement / prevention külön subsystem

A `ReplacementHandler` nem a trigger stack egy speciális esete.

Külön:

- replacement candidate collection;
- replacement layer;
- affected-player/controller döntés;
- optional replacement;
- `hasRun` recursion guard;
- replacement result;
- updated-event újraértékelés;
- prevention;
- skip/can't-happen kezelés

létezik.

A candidate filter többek között ellenőrzi:

- event típust;
- layert;
- zónát;
- requirementet;
- `canReplace` feltételt;
- azt, hogy ugyanaz a replacement ne fusson újra tiltott módon.

A rendszer LKI/future-state modellt is használ olyan eseménynél, ahol a replacement eldöntéséhez az objektum várható állapotát kell vizsgálni.

## AETERNA-következtetés

A replacement/prevention:

```text
nem trigger,
nem reakció,
nem normál stack entry,
hanem az esemény végrehajtása előtti/interceptáló szabályréteg.
```

Ez különösen fontos az OQ-LA-002 megmaradt prevention/replacement kapujához.

---

# 9. Amit érdemes átvenni elvi mintaként

1. trigger detection és trigger scheduling különválasztása;
2. waiting/delayed trigger mint explicit állapot;
3. simultaneous trigger batch mint külön állapot;
4. order meghatározása resolution előtt;
5. stack külön a trigger registrytől;
6. resolution-time revalidation;
7. replacement/prevention külön event-interception réteg;
8. recursion/re-entry guard replacementnél;
9. stable boundary / frozen-stack jellegű orchestration elv;
10. loop guardok és diagnosztikai védelem.

---

# 10. Amit nem szabad közvetlenül átvenni

1. Magic-specifikus APNAP és stack rules;
2. nagy örökölt objektumgráf;
3. mutable `Map<AbilityKey,Object>` payload mint AETERNA contract;
4. játék-specifikus LKI implementáció részletei;
5. GPL kód;
6. konkrét osztály- vagy API-nevek másolása.

AETERNA számára typed C# state, typed event és contract-first modell szükséges.

---

# 11. AETERNA Reaction/Priority következtetések

A jelen audit alapján a minimal Reaction/Priority foundationnek nem szabad egyetlen általános „pending effects” listával helyettesítenie az összes rules lifecycle-t.

Legalább fogalmilag külön kell maradnia:

- trigger batch;
- reaction window;
- resolution stack;
- replacement/prevention evaluation;
- user choice.

Ezek fölött lehet közös coordinator, de a szemantikájuk eltér.

---

# 12. Nyitott kérdések

A teljes Forge-audithoz később külön vizsgálható:

- priority/pass teljes lifecycle;
- event bus és UI projection;
- GameSnapshot és rollback;
- continuous/static effect dependency;
- combat pipeline;
- tests és scenario harness;
- replay/save modell.

---

# 13. Döntés

- **Rules-engine synthesis érték:** P0
- **Közvetlen kódátvétel:** nem
- **Clean-room architecture inspiráció:** igen
- **Reaction/Priority relevancia:** nagyon magas
- **Replacement/prevention relevancia:** nagyon magas
- **További teljes audit:** indokolt, de a jelen targeted audit elegendő a mostani synthesis témához.
