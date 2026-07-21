# AETERNA Game Engine – Tanulóprogram-audit és licencleltár sablon

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.1  
**Dátum:** 2026-07-20  
**Státusz:** aktív általános read-only audit- és licencleltár-sablon  
**Kapcsolódó architektúra:** `ARCHITECTURE.md`

Ez a dokumentum külső programok, repositoryk, mintaprojektek és tanulási források biztonságos vizsgálati sablonja.

A runtime-nyelvi döntés lezárult, ezért a sablon már nem döntési kapu.

Továbbra is használható:

- új könyvtár vagy framework értékelésére;
- packaging- és CI-minta vizsgálatára;
- licenc- és attributionleltárra;
- clean-room architektúraminta kinyerésére;
- külső kódátvétel kockázatának felmérésére.

---

## 1. Kötelező munkarend

1. Read-only leltár.
2. A külső projektben nincs módosítás.
3. Külső kód, asset vagy dokumentum nem kerül automatikusan az AETERNA repositoryba.
4. Minden tényhez forrásbizonyíték.
5. Tény, következtetés és javaslat külön.
6. Kód-, asset-, font-, zene- és dokumentációlicenc külön.
7. Bizonytalan licenc esetén nincs átvétel.
8. Clean-room minta és konkrét implementáció külön.
9. Közvetlen átvételhez explicit emberi jóváhagyás.
10. Az audit nem módosít canonical AETERNA szabályt vagy architektúrát.

---

## 2. Projekttörzsadatok

- **Audit_ID:**
- **Projekt neve:**
- **Repository / hivatalos forrás:**
- **Helyi mappa:**
- **Audit dátuma:**
- **Auditáló:**
- **Vizsgálat típusa:** `read_only`

### Verzió

- **Commit SHA:**
- **Tag / release:**
- **Branch:**
- **Utolsó releváns commit dátuma:**
- **Projekt állapota:** `active | maintenance | experimental | archived | unknown`
- **Godot-verzió:**
- **Python-verzió:**
- **.NET-verzió:**
- **Egyéb runtime:**

### Bizonyíték

- README:
- hivatalos dokumentáció:
- buildleírás:
- release:
- licence:
- dependency manifest:
- CI:
- demo/example:

---

## 3. Licencleltár

### Fő kód

- licenc neve;
- licence file;
- copyright;
- attribution;
- notice;
- módosítási kötelezettség;
- source disclosure;
- redistribution;
- commercial use;
- kompatibilitás.

### Függőségek

| Függőség | Verzió | Forrás | Licenc | Runtime/build | Redistribution | Megjegyzés |
|---|---|---|---|---|---|---|

### Assetek

| Asset | Típus | Forrás | Licenc | Attribution | Átvehető |
|---|---|---|---|---|---|

### Kockázat

- `clear`;
- `review_required`;
- `incompatible`;
- `unknown`;
- `do_not_use`.

---

## 4. Technológiai térkép

- authoritative state helye;
- szabálylogika helye;
- UI helye;
- data source;
- serializer;
- transport;
- process topology;
- startup/shutdown;
- packaging;
- save/log;
- testing;
- deterministic behavior;
- hidden-information;
- AI/batch kapcsolat.

A jelen AETERNA architektúrához viszonyítandó:

- Godot/GDScript visual;
- C# authority;
- Python external tooling.

---

## 5. Build és futtatás

Rögzítendő:

- támogatott OS;
- szükséges SDK;
- runtime prerequisite;
- build parancs;
- output;
- portable/self-contained;
- adminjog;
- offline működés;
- startup;
- shutdown;
- orphan process;
- listener;
- logs;
- clean machine proof.

---

## 6. Tesztelés

- unit;
- integration;
- smoke;
- headless;
- visual/manual;
- CI;
- deterministic test;
- negative test;
- performance;
- soak;
- packaging.

---

## 7. Clean-room hasznosítás

Külön listázandó:

### Átvehető elv

- absztrakt minta;
- project-határ;
- lifecycle-elv;
- tesztelési minta;
- schema-elv;
- packaging-elv.

### Nem vehető át automatikusan

- konkrét kód;
- asset;
- licence nélküli rész;
- szerzői dokumentáció;
- védjegy;
- nem kompatibilis dependency.

### Saját újraalkotási terv

- AETERNA-követelmény;
- független specifikáció;
- saját implementáció;
- saját teszt;
- attribution, ha szükséges.

---

## 8. Eredmény

### Bizonyított tények

- ...

### Következtetések

- ...

### Hasznos AETERNA-minták

- ...

### Kockázatok

- ...

### Döntés

- `use_pattern`;
- `research_more`;
- `defer`;
- `reject`;
- `license_review`;
- `direct_use_requires_approval`.

### Következő lépés

- ...

---

## 9. Repository-biztonság

Külső projekt:

- ne kerüljön az AETERNA repositoryba teljes másolatként;
- ne kerüljön stage-be;
- ne keveredjen saját kóddal;
- ne kerüljön generált build-outputtal együtt;
- szükség esetén külön, Git által nem követett tanulási mappában maradjon.

A sablon nem aktív fejlesztési blocker; csak akkor használjuk, amikor új külső forrást ténylegesen vizsgálunk.
