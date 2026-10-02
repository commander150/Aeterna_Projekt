# AETERNA Game Engine – Tanulóprogram-audit prioritási sor

## VERZIÓ / DOKUMENTUMSTÁTUSZ

**Dokumentumverzió:** 1.2  
**Dátum:** 2026-07-20  
**Státusz:** lezárt történeti auditqueue és technológiai döntés-előkészítési referencia  
**Kapcsolódó lezárt kapu:** `RUNTIME_ENGINE_LANGUAGE_DECISION_GATE.md`

Ez a dokumentum a runtime-nyelvi döntés előtti külső tanulóprogram-audit tervezett sorrendjét őrzi.

Nem aktív tasklista.

A runtime-nyelvi kapu lezárult:

- Python-sidecar proof elkészült és befagyasztva;
- C# in-process proof elkészült és elfogadva;
- C# lett a production authority.

Ezért a teljes korábbi auditqueue végrehajtása nem előfeltétele a C.5B production engine foundationnek.

---

## 1. Eredeti cél

Az auditqueue célja volt:

- Python–Godot és C# runtime-minták vizsgálata;
- portable Windows megoldások összehasonlítása;
- state authority felismerése;
- process/bridge/lifecycle vizsgálata;
- licenc és attribution ellenőrzése;
- clean-room minták kigyűjtése.

A közvetlen technológiai döntéshez szükséges bizonyítékot végül saját AETERNA proofok adták.

---

## 2. Eredeti batchmodell

### Batch 0

Helyi programleltár.

### Batch 1

Közvetlen Python–Godot bridge és sidecar minták.

### Batch 2

Godot .NET/C# és külön rules library minták.

### Batch 3

GDScript rules-service lehetőségek.

### Batch 4

Embedded Python/GDExtension.

### Batch 5

AI, simulation és packaging kiegészítő minták.

A későbbi batch nem indult automatikusan, ha korábbi proof már elég döntési információt adott.

---

## 3. Jelenlegi minősítés

### Már nem szükséges döntési kapuként

- általános Python vs C# nyelvválasztás;
- új GDScript authority proof;
- embedded Python proof;
- production Python-sidecar proof.

### Továbbra is hasznos lehet célzott kutatásként

- Godot .NET production export;
- self-contained Windows packaging;
- C# unit/integration testing;
- CI;
- profiler és performance;
- crash/log reporting;
- save/replay;
- AI headless controller;
- installer és code signing.

Ezekhez az általános auditsablon használható.

---

## 4. Aktiválási szabály

Új külső projekt-audit csak akkor induljon, ha:

- konkrét AETERNA-problémát oldhat meg;
- nincs már saját bizonyíték;
- a kutatás költsége arányos;
- a licenc ellenőrizhető;
- a várható kimenet pontos;
- nem helyettesíti a saját build/teszt bizonyítást.

Minden audit végén:

- `use_pattern`;
- `research_more`;
- `defer`;
- `reject`

döntés készül.

---

## 5. Történeti megőrzés

A korábbi részletes batchsorrend a Git-történetben megmarad.

A working tree-ben ez a rövid változat azért marad, hogy:

- visszakereshető legyen a döntési folyamat;
- ne tűnjön aktív blokkoló feladatnak;
- a licenc- és clean-room elvek megmaradjanak;
- célzott későbbi kutatásnál legyen kiindulópont.

Aktív audit-sablon:

- `LEARNING_PROJECT_AUDIT_AND_LICENSE_TEMPLATE.md`.
