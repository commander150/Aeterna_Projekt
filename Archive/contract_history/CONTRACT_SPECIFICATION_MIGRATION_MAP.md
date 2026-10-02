# AETERNA Game Engine – Contract Specification Migration Map

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2  
**Dátum:** 2026-07-20  
**Státusz:** történeti konszolidációs és későbbi migration-reference  
**Aktív specifikáció:** `CONTRACT_SPECIFICATION.md` 1.5  
**Aktuális státusz:** `CONTRACT_STATUS.md` 1.1  
**Aktuális repository-bázis:** `8e5ee64e42e1657e10f3413444bb870524ee07f9`

Ez a dokumentum nem aktív napi contractlista.

Feladata:

- megőrizni a korábbi konszolidációk eredményét;
- jelezni, mi került az aktív contract-specifikációba;
- megakadályozni, hogy régi sample vagy Python-specifikus mezőlista újra canonical sémának tűnjön;
- kijelölni a következő migration-kör indítási feltételeit.

Elsődleges aktív források:

1. hivatalos játékszabály;
2. `OPEN_QUESTIONS_DECISIONS.md`;
3. `CONTRACT_SPECIFICATION.md`;
4. `CONTRACT_STATUS.md`;
5. elfogadott fixture és teszt;
6. jelen történeti migration map.

---

## 1. Első konszolidációs kör

Korábban átvezetett fő területek:

- contract-first alapelv;
- MatchState authority;
- card definition és instance elhatárolása;
- owner/controller;
- zone/index/sequence;
- activity state;
- Domain topology és occupancy;
- player-visible snapshot;
- hidden information;
- legal action authority;
- action request/response;
- expected state version;
- rejected action no-mutation;
- typed event;
- AI episode;
- Wellspring isolated state és resource summary;
- diagnostics és validation elvek;
- ability registry foundation.

A sample Godot fixture-ek `debug_fixture` státuszt kaptak.

---

## 2. Runtime-nyelvi döntés utáni migráció

2026-07-20-i lezárt döntés:

- production authority: C#/.NET;
- Godot/GDScript: visual client;
- Python: external tooling és reference.

Következmény:

- a contract jelentése technológiafüggetlen marad;
- Python dict/JSON formája nem kötelező C# belső objektumforma;
- a production C# API typed contractokat kap;
- a Python reference output fixture-orákulum;
- a C# candidate proof contractjai nem automatikusan production publikus API-k;
- GDScript nem tart fenn parallel authoritative contractot.

---

## 3. Snapshot migration

Átvezetett:

- viewer-specifikus player-visible snapshot;
- debug snapshot külön;
- own hand visible;
- opponent hand redacted;
- deck count-only;
- public Domain;
- fair AI = player view;
- internal state leak tiltása.

Újabb döntés:

- saját Wellspring identity owner-visible;
- ellenfél Wellspring identity redacted;
- Magnitúdó és activity-count public;
- snapshot nem teljes event log.

Későbbi migration:

- Pecsét state;
- face-down Jel;
- pending decision teljes schema;
- spectator;
- replay.

---

## 4. Legal action és request migration

Átvezetett:

- engine számít legal actiont;
- frontend/AI nem találgat;
- enabled player-facing;
- disabled debug;
- state-version guard;
- snapshot-scoped action ID;
- structured reject;
- no mutation.

Újabb decision:

- production C# `SubmitAction`;
- request ID kötelező;
- source/target/payment payload;
- complex choice pending state;
- bridge rules logic nélkül.

Későbbi migration:

- reaction;
- targeting;
- payment;
- combat;
- partial resolution.

---

## 5. Event migration

Átvezetett:

- ordered typed event;
- `zone_move`;
- `turn_transition`;
- player-visible és debug projection;
- hidden-information policy.

Későbbi:

- activity;
- infusion;
- payment;
- card played;
- entry;
- reaction;
- combat;
- ward;
- victory;
- ability.

A generic `action_resolved` nem kötelező aktív esemény.

---

## 6. Wellspring és resource migration

Átvezetett isolated contract:

- player Wellspring state;
- card count;
- active/exhausted count;
- magnitude = count;
- available Aura = active count.

Döntés:

- normál infusion face-down és active;
- ugyanabban a körben fizethet;
- paymentkor exhausted;
- owner-visible identity;
- opponent redacted identity.

Production migration:

- C.5B után;
- PlayerState;
- MatchState;
- invariant;
- projection;
- infusion;
- payment.

---

## 7. Package és definition migration

A runtime package:

- static definition layer;
- nem MatchState;
- nem card instance;
- nem snapshot.

Production C#:

- package loader;
- typed definitions;
- saját instance létrehozás;
- compatibility validation.

Régi sample identity nem production-final.

---

## 8. Ability migration

Átvezetett:

- registry és support foundation;
- effect tag nem executable;
- fallback kivétel;
- module schema és test követelmény;
- core timing + ability hook;
- keyword registry irány.

Későbbi:

- C# executor;
- first supported modules;
- execution plan;
- coverage;
- reaction/prevention/replacement.

---

## 9. Superseded contractok

Történeti:

- `engine-player-visible-snapshot-v1`;
- `minimal-card-instance-record-v0`;
- korai sample legal action;
- korai sample event;
- fixture-specifikus candidate output modellek;
- Python-only belső helperdict, ha production API-ként volt értelmezve.

Ezek nem törlendők automatikusan a fixture- vagy Git-történetből.

---

## 10. Következő migration-kör indítási feltétele

Új teljes contract-migrációs kör akkor szükséges, ha:

- C.5B production API elkészült;
- Wellspring/infusion/payment vertical slice elkészült;
- `play_card` és Entity placement működik;
- reaction vagy combat contract készül;
- Pecsétmodell lezárul;
- ability executor első module-jai elkészülnek;
- replay/save/network contract indul;
- breaking schema változik.

Kis compatible bővítéshez nem kell új nagy migration map.

---

## 11. Migration-munkarend

1. hivatalos szabálypont;
2. OQ-döntés;
3. contract-spec módosítás;
4. status módosítás;
5. fixture;
6. implementation;
7. tests;
8. Godot/Python adapter;
9. docs links;
10. checkpoint.

Breaking változásnál:

- régi contract;
- új contract;
- compatibility;
- migráció;
- negative test;
- version bump

együtt dokumentálandó.

---

## 12. Dokumentumstátusz

Ez a fájl történeti/reference dokumentum.

Nem:

- következő tasklista;
- aktív state truth;
- production API;
- Open Questions-regiszter.

A végső dokumentumauditban ellenőrizendő, hogy szükséges-e továbbra is a working tree-ben, vagy archiválható a Git-történet és egy rövid migration history mellett.

Addig megőrzendő, mert a contractkonszolidáció és a sample/active elhatárolás visszakereshető forrása.
