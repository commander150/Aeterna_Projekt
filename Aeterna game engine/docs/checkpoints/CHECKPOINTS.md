# AETERNA Game Engine – Mérföldkőnapló

## DOKUMENTUMSTÁTUSZ

- **Dokumentumverzió:** 2.0
- **Dátum:** 2026-07-26
- **Státusz:** append-only történeti technikai mérföldkőnapló
- **Aktuális állapot:** `../../../Aeterna dokumentációk/AETERNA_AKTUALIS_PROJEKTALLAPOT.md`

Ez a fájl nem tasklista és nem specifikáció. Új bejegyzés csak elfogadott, érdemi
mérföldkő után kerül a végére. Régi bejegyzést nem kell az aktuális állapothoz igazítani.

---

## 1. Runtime package és Godot loader alap

Elkészült:

- sample, majd valós runtime package build;
- manifest/cards/decks/lookups/aliases/ability/support/diagnostics;
- Python validáció és publish;
- Godot loader, registry és headless smoke;
- snapshot/legal action/event debug nézetek.

---

## 2. Python minimal reference engine

Meghatározó bázis:

```text
84a7e8f42d313ed58689bbb975c7d6c85ab6e87b
```

Elkészült:

- MatchState és PlayerState;
- expected state version;
- card instance registry;
- draw és end turn;
- typed event;
- player projection;
- Domain reference model;
- activity state;
- izolált Wellspring;
- deterministic AI trajectory.

Aktuális történeti szerep: reference oracle, fixture-, AI- és batch-alap.

---

## 3. Runtime comparison fixture

Fixture:

```text
minimal_draw_end_turn_v1
```

Canonical SHA:

```text
650053262681f79d354867793194a4e49e7862bcccf2475b8cbd34aa03bada6d
```

---

## 4. Python–Godot sidecar proof

Lezáró commit:

```text
d1fb7aaa23d58f166a30f9e0241799f35f5ac14e
```

Státusz: `COMPLETE_AND_FROZEN`.

---

## 5. C# in-process runtime proof

Lezáró commit:

```text
8e5ee64e42e1657e10f3413444bb870524ee07f9
```

Státusz: `COMPLETE_AND_ACCEPTED`.

Bizonyította a pure C# candidate-et, Godot .NET bridge-et, canonical egyezést,
determinism és mutation negative proof alapot.

---

## 6. Runtime-nyelvi döntés

Elfogadva:

- Godot/GDScript = visual client;
- C#/.NET = egyetlen production authority;
- Python = external tooling/reference.

---

## 7. C.5A – Production C# architecture

Státusz: `COMPLETE_AND_ACCEPTED`.

Rögzítette a production projecthatárokat, EngineSessiont, typed contractokat, Godot
bridge-et, Python headless kapcsolatot és az egyetlen C# authorityt.

---

## 8. C.5B – Production C# foundation

Lezáró commit:

```text
931bf5571d541c752aa421a9f0626768bd8ffbe7
```

Státusz: `COMPLETE_AND_ACCEPTED`.

Fő scope:

- pure C# engine;
- headless host;
- test project;
- minimum package loader;
- draw/end-turn;
- stale reject;
- canonical fixture;
- Godot production bridge.

A mérföldkő saját lezárásakor rögzített bizonyíték:

- Debug/Release `13/13`;
- canonical SHA-egyezés;
- `100/100` determinism;
- Godot bridge smoke.

---

## 9. Production Wellspring state és projection

Commit:

```text
9c192abc64445577005e939075a4ab66272ece60
```

Forrásszintű eredmény:

- Wellspring state és invariánsok;
- aktív/kimerült összesítés;
- owner-visible és opponent-redacted projection;
- defensive/non-mutating projection;
- célzott tesztesetek.

A commit aktuális futtatási PASS státusza ebben a dokumentációs körben nem lett újra
bizonyítva.

---

## 10. Production normál Beáramlás

Commit:

```text
3d1d24ac71b839ead7a8d6881237963db48304cb
```

Forrásszintű eredmény:

- `normal_inflow` legal action és typed payload;
- Hand → Wellspring transition;
- egyszer használható körönkénti state;
- stabil rejection reasonök;
- viewer-safe typed event;
- célzott tesztesetek.

---

## 11. Production Magnitúdó-preflight

Commit:

```text
c5a8d343b7f9bdb55d74404a89afdb8ceff51cdb
```

Forrásszintű eredmény:

- runtime Magnitúdó-betöltés és validáció;
- immutable runtime card catalog;
- pure és deterministic Magnitúdó-preflight;
- Wellspring-alapú threshold;
- célzott tesztesetek.

---

## 12. Production Aura-payment preflight

Commit:

```text
5ee20cf199da53818e576726ed378be384d65df6
```

Forrásszintű eredmény:

- runtime lookup catalog;
- Realm/card type normalizálás;
- nyomtatott Aura-költség;
- Aura-payment preflight;
- AETHER és forrásválasztási policy alap;
- selection recheck alap;
- Magnitúdótól elkülönített payment;
- célzott tesztesetek.

---

## 13. Learning kutatási réteg – 15 elkészült audit

Repository HEAD a db0 framework elemzés pótlása után:

```text
78aa464a12eaa4b6c0c53fe042f528e2e82a5fab
```

A learning réteg külső inspiráció és audit. Nem production authority.

A Simeydotme holografikus kutatás eredménye megőrzendő, de a felsorolt fóliaprofilok
nem véglegesek; a rarity-, printing- és artwork-specifikus rendszer később tervezendő.

---

## 14. Dokumentációs működés konszolidációja

Döntés:

- egyetlen aktuális projektállapot;
- egyetlen append-only mérföldkőnapló;
- egy stabil, ritkán változó fájltérkép;
- navigációs README-k;
- a régi státusz- és tervfájlok csak átirányítók.

Cél:

- ne kelljen minden mérföldkő után 8–12 dokumentumot szinkronizálni;
- ne maradjon több egymással versengő aktuális státusz;
- a dokumentáció fenntartása ne vegyen el aránytalan erőforrást a production munkától.

Következő technikai kapu:

- production build- és tesztlánc újrafuttatása;
- utána az egyszerű Entitás-kijátszás legkisebb vertical slice-a.
