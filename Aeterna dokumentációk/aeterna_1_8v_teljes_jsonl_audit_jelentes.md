# AETERNA 1.8v – teljes JSONL adatcsomag audit

Ez a jelentés a feltöltött külön exportált JSONL lapok alapján készült. Nem az azonos nevű XLSX-fájl korábbi verziójára támaszkodik.

## Feldolgozott lapok

- **10. IMPORT_ORIGINAL**: 814 sor
- **11. SETS**: 3 sor
- **12. PRODUCTS**: 22 sor
- **13. CARD_PRINTINGS**: 3 sor
- **14. GENERATION_PROFILES**: 5 sor
- **15. PRODUCT_DECKLISTS**: 754 sor
- **17. NAME_PROFILE**: 814 sor
- **3. CARDS_MASTER**: 814 sor
- **4. AUDIT_LOG**: 185 sor
- **5. LOOKUPS**: 29 sor
- **6. RARITY_CODES**: 6 sor
- **8. EXPORT_NOTES**: 1 sor
- **9. DECISION_LOG**: 133 sor


## Ellenőrzési korlát

A csomagban nem szerepelt külön VERZIÓ lap exportja, ezért az 1.8v verziósor tényleges meglétét ebből a JSONL-csomagból nem lehetett ellenőrizni.

## Gyors állapotkép

- CARDS_MASTER kártyák: 814
- Egyedi Szabályi_Kártya_ID: 814
- NAME_PROFILE sorok: 814
- PRODUCT_DECKLISTS sorok: 754
- Talált fő hiba/javítási kategóriák száma: 22

## Prioritási jelmagyarázat

- **P1**: kötelező adatkonzisztencia / validációs javítás
- **P2**: fontos workflow-, lookup-, szinkron- vagy tisztítási javítás
- **P3**: nem blokkoló, de későbbi szerkezeti vagy döntési pont

## Összesített hibák és javítandó pontok

### 1. [P1] CARDS_MASTER/LOOKUPS – Audit_Státusz érték nincs LOOKUPS-ban (Audit státuszok)

- `token szabály átvezetve`: 2 tétel. Példák: AET-IGN-HAM-023, AET-IGN-HAM-031
- `javítva`: 53 tétel. Példák: AET-AQU-ART-001, AET-AQU-ART-002, AET-AQU-ART-003, AET-AQU-ART-004, AET-AQU-ART-005, AET-AQU-ART-006, AET-AQU-ART-007, AET-AQU-ART-008, AET-AQU-ART-009, AET-AQU-ART-010, AET-AQU-ART-011, AET-AQU-ART-012, AET-AQU-ART-013, AET-AQU-ART-014, AET-AQU-ART-015 (+38 további)
- `szövegjavított_tesztelendő`: 301 tétel. Példák: AET-LUX-FHL-001, AET-LUX-FHL-002, AET-LUX-FHL-003, AET-LUX-FHL-004, AET-LUX-FHL-005, AET-LUX-FHL-015, AET-LUX-FHL-028, AET-LUX-FHL-029, AET-LUX-FHL-030, AET-LUX-FHL-032, AET-LUX-FHL-033, AET-LUX-FHL-046, AET-LUX-FHL-049, AET-LUX-FHL-050, AET-LUX-FHL-051 (+286 további)
- `átalakított_tesztelendő`: 5 tétel. Példák: AET-UMB-ARS-044, AET-UMB-ARS-052, AET-UMB-ARS-058, AET-UMB-LEA-008, AET-UMB-LEA-044
- `szövegjavított_structured_javított_tesztelendő`: 1 tétel. Példák: AET-UMB-ARS-051
- `tiszta`: 1 tétel. Példák: AET-UMB-LEA-019
- `adatjavított`: 3 tétel. Példák: AET-AET-FGS-001, AET-AET-KOB-020, AET-AET-KOB-023
- `szövegjavított_review`: 47 tétel. Példák: AET-AET-FGS-013, AET-AET-FGS-026, AET-AET-FGS-028, AET-AET-FGS-030, AET-AET-FGS-033, AET-AET-FGS-036, AET-AET-FGS-037, AET-AET-FGS-040, AET-AET-FGS-041, AET-AET-FGS-045, AET-AET-FGS-046, AET-AET-FGS-050, AET-AET-FGS-052, AET-AET-FGS-055, AET-AET-FGS-056 (+32 további)

### 2. [P1] CARDS_MASTER/LOOKUPS – Klán érték nincs LOOKUPS-ban (Alapjátékos Klánok)

- `Ős-Druidák`: 58 tétel. Példák: AET-TER-DRU-001, AET-TER-DRU-002, AET-TER-DRU-003, AET-TER-DRU-004, AET-TER-DRU-005, AET-TER-DRU-006, AET-TER-DRU-007, AET-TER-DRU-008, AET-TER-DRU-009, AET-TER-DRU-010, AET-TER-DRU-011, AET-TER-DRU-012, AET-TER-DRU-013, AET-TER-DRU-014, AET-TER-DRU-015 (+43 további)
- `Égbolt Úrai`: 58 tétel. Példák: AET-VEN-EGU-001, AET-VEN-EGU-002, AET-VEN-EGU-003, AET-VEN-EGU-004, AET-VEN-EGU-005, AET-VEN-EGU-006, AET-VEN-EGU-007, AET-VEN-EGU-008, AET-VEN-EGU-009, AET-VEN-EGU-010, AET-VEN-EGU-011, AET-VEN-EGU-012, AET-VEN-EGU-013, AET-VEN-EGU-014, AET-VEN-EGU-015 (+43 további)

### 3. [P1] CARDS_MASTER/LOOKUPS – Play_Legal_Status érték nincs LOOKUPS-ban (Play Legal Status értékek)

- `CORE01_review_required`: 123 tétel. Példák: AET-UMB-ARS-008, AET-UMB-ARS-009, AET-UMB-ARS-012, AET-UMB-ARS-013, AET-UMB-ARS-014, AET-UMB-ARS-015, AET-UMB-ARS-029, AET-UMB-ARS-030, AET-UMB-ARS-037, AET-UMB-ARS-038, AET-UMB-ARS-039, AET-UMB-ARS-040, AET-UMB-ARS-049, AET-UMB-ARS-051, AET-UMB-ARS-054 (+108 további)

### 4. [P1] CARDS_MASTER/LOOKUPS – Rarity érték nincs LOOKUPS-ban (Rarity kódok)

- `U`: 58 tétel. Példák: AET-AET-FGS-003, AET-AET-FGS-004, AET-AET-FGS-006, AET-AET-FGS-009, AET-AET-FGS-011, AET-AET-FGS-016, AET-AET-FGS-017, AET-AET-FGS-020, AET-AET-FGS-021, AET-AET-FGS-022, AET-AET-FGS-023, AET-AET-FGS-024, AET-AET-FGS-032, AET-AET-FGS-033, AET-AET-FGS-034 (+43 további)

### 5. [P1] CARDS_MASTER/RARITY – Rarity=U, miközben LOOKUPS/RARITY_CODES szerint UC van

Összesen: 58 tétel.

- AET-AET-FGS-003 | CORE01-AET-FGS-003-U-NF-A1-V1 | Lopakodó Felcser-Drón
- AET-AET-FGS-004 | CORE01-AET-FGS-004-U-NF-A1-V1 | Bronzfal Gólem
- AET-AET-FGS-006 | CORE01-AET-FGS-006-U-NF-A1-V1 | Aether-Generátor
- AET-AET-FGS-009 | CORE01-AET-FGS-009-U-NF-A1-V1 | Páncélozott Juggernaut
- AET-AET-FGS-011 | CORE01-AET-FGS-011-U-NF-A1-V1 | Újrahasznosító Egység
- AET-AET-FGS-016 | CORE01-AET-FGS-016-U-NF-A1-V1 | Fémkereső Robotkutya
- AET-AET-FGS-017 | CORE01-AET-FGS-017-U-NF-A1-V1 | Olajozó Drón
- AET-AET-FGS-020 | CORE01-AET-FGS-020-U-NF-A1-V1 | Páncélkovács Mester
- AET-AET-FGS-021 | CORE01-AET-FGS-021-U-NF-A1-V1 | Gyár-Felügyelő
- AET-AET-FGS-022 | CORE01-AET-FGS-022-U-NF-A1-V1 | Rakétás Drón
- AET-AET-FGS-023 | CORE01-AET-FGS-023-U-NF-A1-V1 | Mechanikus Skorpió
- AET-AET-FGS-024 | CORE01-AET-FGS-024-U-NF-A1-V1 | Réz Gólem
- AET-AET-FGS-032 | CORE01-AET-FGS-032-U-NF-A1-V1 | Túlvezérelt Védőmező
- AET-AET-FGS-033 | CORE01-AET-FGS-033-U-NF-A1-V1 | Célzó Szoftver
- AET-AET-FGS-034 | CORE01-AET-FGS-034-U-NF-A1-V1 | Fémolvasztó Sugár
- AET-AET-FGS-036 | CORE01-AET-FGS-036-U-NF-A1-V1 | Vészhelyzeti Gyorsítás
- AET-AET-FGS-037 | CORE01-AET-FGS-037-U-NF-A1-V1 | Rendszer-Kalibrálás
- AET-AET-FGS-039 | CORE01-AET-FGS-039-U-NF-A1-V1 | Fogaskerék-Olajozás
- AET-AET-FGS-040 | CORE01-AET-FGS-040-U-NF-A1-V1 | Túlterhelés
- AET-AET-FGS-042 | CORE01-AET-FGS-042-U-NF-A1-V1 | Szegecsvihar
- AET-AET-FGS-043 | CORE01-AET-FGS-043-U-NF-A1-V1 | Gépiesítés
- AET-AET-FGS-044 | CORE01-AET-FGS-044-U-NF-A1-V1 | Alkatrész-Gyűjtés
- AET-AET-FGS-047 | CORE01-AET-FGS-047-U-NF-A1-V1 | Védelmi Mátrix
- AET-AET-FGS-048 | CORE01-AET-FGS-048-U-NF-A1-V1 | Rövidzárlat
- AET-AET-FGS-049 | CORE01-AET-FGS-049-U-NF-A1-V1 | Túlhevült Kazán
- AET-AET-FGS-052 | CORE01-AET-FGS-052-U-NF-A1-V1 | Rejtett Aknák
- AET-AET-FGS-053 | CORE01-AET-FGS-053-U-NF-A1-V1 | Vészhelyzeti Védőpajzs
- AET-AET-FGS-054 | CORE01-AET-FGS-054-U-NF-A1-V1 | Önmegsemmisítő Protokoll
- AET-AET-FGS-057 | CORE01-AET-FGS-057-U-NF-A1-V1 | A Hulladéktelep
- AET-AET-FGS-058 | CORE01-AET-FGS-058-U-NF-A1-V1 | A Nagy Óramű Műhely
- AET-AET-KOB-003 | CORE01-AET-KOB-003-U-NF-A1-V1 | Kincskereső Kalandor
- AET-AET-KOB-004 | CORE01-AET-KOB-004-U-NF-A1-V1 | Árnyékos Sikátor Csempésze
- AET-AET-KOB-006 | CORE01-AET-KOB-006-U-NF-A1-V1 | Szerencsevadász Kalandor
- AET-AET-KOB-009 | CORE01-AET-KOB-009-U-NF-A1-V1 | Szabadúszó Mágus
- AET-AET-KOB-010 | CORE01-AET-KOB-010-U-NF-A1-V1 | Univerzális Tudós
- AET-AET-KOB-011 | CORE01-AET-KOB-011-U-NF-A1-V1 | Karaván Őrparancsnok
- AET-AET-KOB-016 | CORE01-AET-KOB-016-U-NF-A1-V1 | Utazó Bárd
- AET-AET-KOB-019 | CORE01-AET-KOB-019-U-NF-A1-V1 | Talizmán-Árus
- AET-AET-KOB-021 | CORE01-AET-KOB-021-U-NF-A1-V1 | Informátor
- AET-AET-KOB-022 | CORE01-AET-KOB-022-U-NF-A1-V1 | Csempész-Hajós
- AET-AET-KOB-024 | CORE01-AET-KOB-024-U-NF-A1-V1 | Fejvadász Nindzsa
- AET-AET-KOB-025 | CORE01-AET-KOB-025-U-NF-A1-V1 | Gazdag Kereskedő
- AET-AET-KOB-033 | CORE01-AET-KOB-033-U-NF-A1-V1 | Szerencsés Találat
- AET-AET-KOB-035 | CORE01-AET-KOB-035-U-NF-A1-V1 | Hirtelen Kitérő
- AET-AET-KOB-036 | CORE01-AET-KOB-036-U-NF-A1-V1 | Gyors Szerződés
- AET-AET-KOB-037 | CORE01-AET-KOB-037-U-NF-A1-V1 | Kitérő Manőver
- AET-AET-KOB-038 | CORE01-AET-KOB-038-U-NF-A1-V1 | Információ-Vásárlás
- AET-AET-KOB-039 | CORE01-AET-KOB-039-U-NF-A1-V1 | Fogadó a Keresztútnál
- AET-AET-KOB-040 | CORE01-AET-KOB-040-U-NF-A1-V1 | Adósság Behajtása
- AET-AET-KOB-044 | CORE01-AET-KOB-044-U-NF-A1-V1 | Feketepiac
- AET-AET-KOB-046 | CORE01-AET-KOB-046-U-NF-A1-V1 | Zsoldos Szerződés
- AET-AET-KOB-047 | CORE01-AET-KOB-047-U-NF-A1-V1 | Hamis Arany
- AET-AET-KOB-048 | CORE01-AET-KOB-048-U-NF-A1-V1 | Kígyóverem
- AET-AET-KOB-049 | CORE01-AET-KOB-049-U-NF-A1-V1 | Meglepetésszerű Ellenakció
- AET-AET-KOB-052 | CORE01-AET-KOB-052-U-NF-A1-V1 | Vámszedő Pont
- AET-AET-KOB-053 | CORE01-AET-KOB-053-U-NF-A1-V1 | Váratlan Erősítés
- AET-AET-KOB-054 | CORE01-AET-KOB-054-U-NF-A1-V1 | Hamis Ígéret
- AET-AET-KOB-057 | CORE01-AET-KOB-057-U-NF-A1-V1 | Rejtett Oázis

### 6. [P1] NAME_PROFILE – mezőeltérés CARDS_MASTER-hez képest

Összesen: 24 tétel.

- AET-IGN-HAM-009 | Faj | Ember vagy Ork | Ember
- AET-IGN-HAM-010 | Faj | Ember vagy Ork | Ember
- AET-IGN-HAM-010 | Kaszt | Orgyilkos / Harcos | Orgyilkos
- AET-IGN-HAM-012 | Kaszt | Harcos vagy Őrző | Őrző
- AET-IGN-LAN-004 | Kaszt | Alap | Mágus
- AET-IGN-LAN-006 | Kaszt | Alap | Kósza
- AET-LUX-FHL-021 | Kaszt | Alap | Vadász
- AET-LUX-FHL-024 | Kaszt | Alap | Őrző
- AET-LUX-FHL-026 | Kaszt | Alap | Harcos
- AET-LUX-FHL-029 | Kaszt | Alap | Őrző
- AET-LUX-APJ-003 | Kaszt | Alap | Kósza
- AET-LUX-APJ-005 | Kaszt | Alap | Őrző
- AET-LUX-APJ-009 | Kaszt | Alap | Őrző
- AET-LUX-APJ-023 | Kaszt | Alap | Őrző
- AET-LUX-APJ-029 | Kaszt | Alap | Őrző
- AET-LUX-APJ-030 | Kaszt | Alap | Őrző
- AET-VEN-VIH-011 | Kaszt | Kósza | Vadász
- AET-VEN-VIH-023 | Kaszt | Kósza | Vadász
- AET-VEN-VIH-027 | Kaszt | Kósza | Mágus
- AET-VEN-VIH-030 | Kaszt | Kósza | Harcos
- AET-VEN-EGU-008 | Kaszt | Kósza | Mágus
- AET-VEN-EGU-011 | Kaszt | Kósza | Harcos
- AET-VEN-EGU-021 | Kaszt | Kósza | Harcos
- AET-VEN-EGU-029 | Kaszt | Kósza | Hős

### 7. [P1] PRODUCT_DECKLISTS – Pakli összeg nem 40 lap

Összesen: 3 tétel.

- BKP-AQU01 | DECK-AQU-STARTER-001 | 41
- TEST-CORE01-LUX | DECK-LUX-FHL-TEST-001 | 41
- TEST-CORE01-TERRA | DECK-TER-DRU-TEST-001 | 41

### 8. [P2] 12. PRODUCTS – teljesen üres / none sorok

Összesen: 5 tétel.

- 18
- 19
- 20
- 21
- 22

### 9. [P2] CARDS_MASTER – structured mezőkben régi/rossz tokenek: trap/burst

Összesen: 42 tétel.

- AET-IGN-HAM-039 | Kulcsszavak_Felismerve | burst
- AET-IGN-HAM-040 | Kulcsszavak_Felismerve | burst
- AET-IGN-HAM-043 | Kulcsszavak_Felismerve | burst
- AET-IGN-HAM-045 | Kulcsszavak_Felismerve | burst
- AET-IGN-LAN-039 | Kulcsszavak_Felismerve | burst
- AET-IGN-LAN-040 | Kulcsszavak_Felismerve | burst
- AET-IGN-LAN-044 | Kulcsszavak_Felismerve | burst
- AET-IGN-LAN-046 | Kulcsszavak_Felismerve | burst
- AET-AQU-MOR-039 | Kulcsszavak_Felismerve | burst
- AET-AQU-MOR-042 | Kulcsszavak_Felismerve | aegis, burst
- AET-AQU-MOR-043 | Kulcsszavak_Felismerve | burst
- AET-AQU-MOR-046 | Kulcsszavak_Felismerve | burst
- AET-AQU-ART-040 | Kulcsszavak_Felismerve | burst
- AET-AQU-ART-045 | Kulcsszavak_Felismerve | burst
- AET-AQU-ART-047 | Kulcsszavak_Felismerve | burst
- AET-TER-DRU-031 | Kulcsszavak_Felismerve | aegis, burst
- AET-TER-DRU-037 | Kulcsszavak_Felismerve | burst
- AET-TER-WHU-031 | Kulcsszavak_Felismerve | burst
- AET-TER-WHU-036 | Kulcsszavak_Felismerve | burst
- AET-TER-WHU-037 | Kulcsszavak_Felismerve | aegis, burst
- AET-TER-WHU-038 | Kulcsszavak_Felismerve | burst
- AET-LUX-FHL-031 | Kulcsszavak_Felismerve | burst
- AET-LUX-FHL-032 | Kulcsszavak_Felismerve | burst
- AET-LUX-FHL-035 | Kulcsszavak_Felismerve | burst
- AET-LUX-APJ-031 | Kulcsszavak_Felismerve | burst
- AET-LUX-APJ-036 | Kulcsszavak_Felismerve | burst
- AET-LUX-APJ-037 | Kulcsszavak_Felismerve | burst
- AET-UMB-ARS-031 | Kulcsszavak_Felismerve | burst
- AET-UMB-ARS-033 | Kulcsszavak_Felismerve | burst
- AET-UMB-ARS-038 | Kulcsszavak_Felismerve | burst
- AET-UMB-LEA-031 | Kulcsszavak_Felismerve | burst
- AET-UMB-LEA-032 | Kulcsszavak_Felismerve | burst
- AET-UMB-LEA-035 | Kulcsszavak_Felismerve | burst
- AET-VEN-VIH-036 | Kulcsszavak_Felismerve | burst
- AET-VEN-EGU-035 | Kulcsszavak_Felismerve | burst
- AET-VEN-EGU-036 | Kulcsszavak_Felismerve | burst
- AET-VEN-EGU-037 | Kulcsszavak_Felismerve | burst
- AET-AET-FGS-032 | Kulcsszavak_Felismerve | burst
- AET-AET-FGS-037 | Kulcsszavak_Felismerve | burst
- AET-AET-KOB-031 | Kulcsszavak_Felismerve | burst
- AET-AET-KOB-035 | Kulcsszavak_Felismerve | burst
- AET-AET-KOB-036 | Kulcsszavak_Felismerve | burst

### 10. [P2] CARDS_MASTER/LOOKUPS – Hibakategória token nincs LOOKUPS-ban

- `összetett szabályszöveg`: 1 tétel. Példák: AET-IGN-HAM-009
- `feltétel pontosítása`: 1 tétel. Példák: AET-IGN-HAM-010
- `támadási korlátozás`: 1 tétel. Példák: AET-IGN-HAM-012
- `önsebzéses Riadó`: 1 tétel. Példák: AET-IGN-HAM-013
- `Hős`: 3 tétel. Példák: AET-IGN-HAM-014, AET-IGN-HAM-030, AET-IGN-LAN-030
- `kulcsszó-kombináció`: 3 tétel. Példák: AET-IGN-HAM-014, AET-IGN-HAM-022, AET-IGN-HAM-029
- `Faj-alapú szinergia`: 1 tétel. Példák: AET-IGN-HAM-015
- `Visszhang trigger pontosítás`: 1 tétel. Példák: AET-IGN-HAM-016
- `önsebzéses támadó lap`: 1 tétel. Példák: AET-IGN-HAM-017
- `Riadó önsebzéssel`: 1 tétel. Példák: AET-IGN-HAM-020
- `Harmonizálás-módosító`: 1 tétel. Példák: AET-IGN-HAM-021
- `tokenrendszer státusz rendezve`: 2 tétel. Példák: AET-IGN-HAM-023, AET-IGN-HAM-031
- `régi terminológia javítása`: 1 tétel. Példák: AET-IGN-HAM-024
- `sérülésfüggő buff`: 1 tétel. Példák: AET-IGN-HAM-025
- `Faj-alapú aura`: 1 tétel. Példák: AET-IGN-HAM-026
- `idézési betegség terminológia`: 1 tétel. Példák: AET-IGN-HAM-027
- `tömeges kulcsszóadás`: 2 tétel. Példák: AET-IGN-HAM-027, AET-IGN-HAM-042
- `Kényszerítés célpont pontosítása`: 1 tétel. Példák: AET-IGN-HAM-028
- `blokk-korlátozás`: 1 tétel. Példák: AET-IGN-HAM-029
- `tömeges sebzés`: 1 tétel. Példák: AET-IGN-HAM-030
- `késleltetett önsebzés`: 1 tétel. Példák: AET-IGN-HAM-032
- `Kényszerítés tömeges hatás`: 1 tétel. Példák: AET-IGN-HAM-033
- `token-visszaélés korlátozása`: 1 tétel. Példák: AET-IGN-HAM-034
- `áldozás + lapelőny finomítása`: 1 tétel. Példák: AET-IGN-HAM-034
- `ideiglenes kulcsszóadás`: 2 tétel. Példák: AET-IGN-HAM-036, AET-IGN-HAM-041
- `korábbi Pecsét-logika eltávolítva`: 1 tétel. Példák: AET-IGN-HAM-036
- `feltételes megsemmisítés`: 1 tétel. Példák: AET-IGN-HAM-037
- `Pecsét-célzás eltávolítása`: 2 tétel. Példák: AET-IGN-HAM-038, AET-IGN-HAM-040
- `áldozásos sebzés`: 1 tétel. Példák: AET-IGN-HAM-038
- `Burst Ige`: 5 tétel. Példák: AET-IGN-HAM-039, AET-IGN-HAM-043, AET-IGN-LAN-039, AET-IGN-LAN-044, AET-IGN-LAN-046
- `célzott Kimerítés`: 1 tétel. Példák: AET-IGN-HAM-039
- `Burst sebzés`: 1 tétel. Példák: AET-IGN-HAM-040
- `harci ATK-buff`: 1 tétel. Példák: AET-IGN-HAM-043
- `Burst sebzés sérült célpontra`: 1 tétel. Példák: AET-IGN-HAM-045
- `ideiglenes Oltalom pontosítva`: 1 tétel. Példák: AET-IGN-HAM-046
- `támadó Entitásonként egyszeri delayed sebzés`: 1 tétel. Példák: AET-IGN-HAM-046
- `Jel támadásra reagál`: 1 tétel. Példák: AET-IGN-HAM-047
- `Oltalomhoz kötött Jel`: 1 tétel. Példák: AET-IGN-HAM-048
- `megidézés pontosítása`: 1 tétel. Példák: AET-IGN-HAM-049
- `belépéskori Jel`: 1 tétel. Példák: AET-IGN-HAM-049
- `célpontvalidáció tesztelendő`: 1 tétel. Példák: AET-IGN-HAM-050
- `összetett sebzésképlet egyszerűsítve`: 1 tétel. Példák: AET-IGN-HAM-051
- `fix megtorló sebzés`: 1 tétel. Példák: AET-IGN-HAM-051
- `támadásreakciós Jel`: 1 tétel. Példák: AET-IGN-HAM-052
- `magas sebzés`: 2 tétel. Példák: AET-IGN-HAM-052, AET-IGN-LAN-053
- `játékba kerülésre reagáló Jel`: 1 tétel. Példák: AET-IGN-HAM-053
- `szűkített counterhatás`: 2 tétel. Példák: AET-IGN-HAM-054, AET-IGN-LAN-039
- `Jel-formátum pontosítva`: 1 tétel. Példák: AET-IGN-HAM-054
- `Zenit-korlátozás`: 1 tétel. Példák: AET-IGN-HAM-055
- `támadási buff`: 1 tétel. Példák: AET-IGN-HAM-056
- `költségcsökkentés`: 6 tétel. Példák: AET-IGN-HAM-057, AET-UMB-ARS-008, AET-UMB-ARS-055, AET-VEN-VIH-056, AET-VEN-EGU-018, AET-VEN-EGU-032
- `lapelőny`: 1 tétel. Példák: AET-IGN-HAM-058
- `játékosonkénti limit`: 1 tétel. Példák: AET-IGN-HAM-058
- `Pecsét-hivatkozás eltávolítva`: 1 tétel. Példák: AET-IGN-LAN-001
- `összetett erőforrás-trigger egyszerűsítve`: 1 tétel. Példák: AET-IGN-LAN-001
- `Harmonizálás-kulcsszóadás pontosítása`: 1 tétel. Példák: AET-IGN-LAN-002
- `Ige/Rituálé-trigger`: 1 tétel. Példák: AET-IGN-LAN-002
- `Harmonizálás érték pontosítása`: 2 tétel. Példák: AET-IGN-LAN-003, AET-IGN-LAN-017
- `Riadó sebzés`: 1 tétel. Példák: AET-IGN-LAN-003
- `közvetlen Pecsét-sebzés eltávolítva`: 1 tétel. Példák: AET-IGN-LAN-004
- `Visszhang pontosítva`: 1 tétel. Példák: AET-IGN-LAN-004
- `Zenit-támogató aura`: 1 tétel. Példák: AET-IGN-LAN-005
- `Oltalom-adás`: 1 tétel. Példák: AET-IGN-LAN-005
- `időzített visszatérés`: 1 tétel. Példák: AET-IGN-LAN-006
- `Visszhang pontosítás`: 1 tétel. Példák: AET-IGN-LAN-006
- `Ige/Rituálé célzás pontosítása`: 2 tétel. Példák: AET-IGN-LAN-008, AET-IGN-LAN-021
- `feltételes húzás`: 1 tétel. Példák: AET-IGN-LAN-008
- `Pecsét-sebzés eltávolítva`: 4 tétel. Példák: AET-IGN-LAN-009, AET-IGN-LAN-041, AET-IGN-LAN-047, AET-IGN-LAN-052
- `Ige/Rituálé-trigger sebzés`: 1 tétel. Példák: AET-IGN-LAN-009
- `ingyenes kijátszás`: 1 tétel. Példák: AET-IGN-LAN-010
- `Aura-költség felülírás`: 1 tétel. Példák: AET-IGN-LAN-010
- `halálos sebzés replacement`: 2 tétel. Példák: AET-IGN-LAN-011, AET-IGN-LAN-012
- `Pecsét-sebzés elhatárolása`: 1 tétel. Példák: AET-IGN-LAN-011
- `Üresség-recursion`: 3 tétel. Példák: AET-IGN-LAN-012, AET-IGN-LAN-023, AET-IGN-LAN-038
- `Zenit-sebzés támadási triggerből`: 1 tétel. Példák: AET-IGN-LAN-013
- `Hasítás + célzott Zenit-sebzés`: 1 tétel. Példák: AET-IGN-LAN-014
- `Légies + Rezonancia balansz`: 1 tétel. Példák: AET-IGN-LAN-015
- `költségcsökkentés minimum pontosítása`: 1 tétel. Példák: AET-IGN-LAN-016
- `célzott Horizont-sebzés`: 1 tétel. Példák: AET-IGN-LAN-018
- `Pecsét-feltörés jutalmazása`: 1 tétel. Példák: AET-IGN-LAN-019
- `húzás`: 2 tétel. Példák: AET-IGN-LAN-019, AET-VEN-EGU-048
- `Ige/Rituálé sebzésbónusz`: 1 tétel. Példák: AET-IGN-LAN-020
- `Rezonancia + damage_mod`: 1 tétel. Példák: AET-IGN-LAN-020
- `Oltalom-védőlap`: 1 tétel. Példák: AET-IGN-LAN-021
- `Ige visszavétel`: 1 tétel. Példák: AET-IGN-LAN-023
- `egyszerű Hasítás`: 1 tétel. Példák: AET-IGN-LAN-024
- `Légies + Ige/Rituálé triggerelt ATK-buff`: 1 tétel. Példák: AET-IGN-LAN-025
- `Rezonancia + költségcsökkentés`: 1 tétel. Példák: AET-IGN-LAN-026
- `minimum pontosítás`: 1 tétel. Példák: AET-IGN-LAN-026
- `saját Pecsét megsemmisítése eltávolítva`: 1 tétel. Példák: AET-IGN-LAN-027
- `áldozásos tömeges sebzés`: 1 tétel. Példák: AET-IGN-LAN-027
- `Visszhang`: 1 tétel. Példák: AET-IGN-LAN-028
- `delayed return`: 1 tétel. Példák: AET-IGN-LAN-028
- `Oltalom`: 1 tétel. Példák: AET-IGN-LAN-028
- `statvédelem`: 1 tétel. Példák: AET-IGN-LAN-029
- `Ige/Rituálé pontosítás`: 1 tétel. Példák: AET-IGN-LAN-029
- `ideiglenes Aura`: 1 tétel. Példák: AET-IGN-LAN-030
- `Rezonancia`: 2 tétel. Példák: AET-IGN-LAN-030, AET-UMB-LEA-019
- `többcélpontos sebzés`: 1 tétel. Példák: AET-IGN-LAN-031
- `tömeges Horizont-sebzés`: 1 tétel. Példák: AET-IGN-LAN-032
- `áldozás + lapelőny`: 1 tétel. Példák: AET-IGN-LAN-033
- `Áramlat-alapú tömeges sebzés`: 1 tétel. Példák: AET-IGN-LAN-034
- `áldozás + ideiglenes Aura + húzás finomítva`: 1 tétel. Példák: AET-IGN-LAN-035
- `Magnitúdó-alapú tömeges megsemmisítés`: 1 tétel. Példák: AET-IGN-LAN-036
- `Hard Limit hivatkozás eltávolítva`: 1 tétel. Példák: AET-IGN-LAN-037
- `Elementál-alapú húzás`: 1 tétel. Példák: AET-IGN-LAN-037
- `temető terminológia javítása`: 1 tétel. Példák: AET-IGN-LAN-038
- `Burst cantrip`: 1 tétel. Példák: AET-IGN-LAN-040
- `sebzés + húzás`: 1 tétel. Példák: AET-IGN-LAN-040
- `Áramlaton belüli Zenit-sebzés`: 1 tétel. Példák: AET-IGN-LAN-041
- `Zenit-Horizont mozgatás`: 1 tétel. Példák: AET-IGN-LAN-042
- `ideiglenes ATK-buff`: 1 tétel. Példák: AET-IGN-LAN-042
- `ideiglenes Légies kulcsszóadás`: 1 tétel. Példák: AET-IGN-LAN-043
- `Ige/Rituálé sebzésmegelőzés`: 1 tétel. Példák: AET-IGN-LAN-044
- `tömeges Zenit-sebzésmegelőzés`: 1 tétel. Példák: AET-IGN-LAN-045
- `Kimerült célpont sebzése`: 1 tétel. Példák: AET-IGN-LAN-046
- `extra húzásra reagáló Jel`: 1 tétel. Példák: AET-IGN-LAN-047
- `Zenit-megsemmisülés trigger`: 1 tétel. Példák: AET-IGN-LAN-048
- `tömeges Zenit-sebzés`: 1 tétel. Példák: AET-IGN-LAN-048
- `Aeternal/Pecsét-célzás eltávolítva`: 1 tétel. Példák: AET-IGN-LAN-049
- `sebzésvisszaverés Entitásra`: 1 tétel. Példák: AET-IGN-LAN-049
- `Jel-formátum`: 2 tétel. Példák: AET-IGN-LAN-050, AET-IGN-LAN-051
- `védekező HP-buff`: 1 tétel. Példák: AET-IGN-LAN-050
- `Ige/Rituálé trigger`: 1 tétel. Példák: AET-IGN-LAN-051
- `büntető sebzés`: 1 tétel. Példák: AET-IGN-LAN-051
- `extra húzás büntetése`: 1 tétel. Példák: AET-IGN-LAN-052
- `random discard`: 1 tétel. Példák: AET-IGN-LAN-052
- `Zenit-megsemmisülésre reagáló Jel`: 1 tétel. Példák: AET-IGN-LAN-053
- `Zenitbe játékba kerülésre reagáló Jel`: 1 tétel. Példák: AET-IGN-LAN-054
- `korlátlan költségcsökkentés szűkítve`: 1 tétel. Példák: AET-IGN-LAN-055
- `Sík globális spell-támogatás`: 2 tétel. Példák: AET-IGN-LAN-055, AET-IGN-LAN-056
- `extra Beáramlás eltávolítva`: 1 tétel. Példák: AET-IGN-LAN-056
- `Zenit célzásvédelem`: 1 tétel. Példák: AET-IGN-LAN-057
- `Ige/Rituálé Entitás-sebzés módosítás`: 1 tétel. Példák: AET-IGN-LAN-058
- `Pecsét-elhatárolás javítva`: 2 tétel. Példák: AET-AQU-MOR-014, AET-AQU-MOR-041
- `Faj-hiba`: 3 tétel. Példák: AET-AQU-MOR-022, AET-AQU-MOR-027, AET-AQU-MOR-056
- `alapadat_hiba`: 190 tétel. Példák: AET-AQU-ART-001, AET-AQU-ART-002, AET-AQU-ART-003, AET-AQU-ART-004, AET-AQU-ART-005, AET-AQU-ART-006, AET-AQU-ART-007, AET-AQU-ART-008, AET-AQU-ART-009, AET-AQU-ART-010, AET-AQU-ART-011, AET-AQU-ART-012, AET-AQU-ART-013, AET-AQU-ART-014, AET-AQU-ART-015 (+175 további)
- `szabályszöveg_hiba`: 281 tétel. Példák: AET-AQU-ART-001, AET-AQU-ART-002, AET-AQU-ART-003, AET-AQU-ART-004, AET-AQU-ART-005, AET-AQU-ART-006, AET-AQU-ART-007, AET-AQU-ART-008, AET-AQU-ART-009, AET-AQU-ART-010, AET-AQU-ART-011, AET-AQU-ART-012, AET-AQU-ART-013, AET-AQU-ART-014, AET-AQU-ART-015 (+266 további)
- `structured_mezőhiba`: 365 tétel. Példák: AET-AQU-ART-001, AET-AQU-ART-002, AET-AQU-ART-003, AET-AQU-ART-004, AET-AQU-ART-005, AET-AQU-ART-006, AET-AQU-ART-007, AET-AQU-ART-008, AET-AQU-ART-009, AET-AQU-ART-010, AET-AQU-ART-011, AET-AQU-ART-012, AET-AQU-ART-013, AET-AQU-ART-014, AET-AQU-ART-015 (+350 további)
- `engine_gyanú`: 350 tétel. Példák: AET-AQU-ART-002, AET-AQU-ART-003, AET-AQU-ART-005, AET-AQU-ART-006, AET-AQU-ART-007, AET-AQU-ART-010, AET-AQU-ART-011, AET-AQU-ART-012, AET-AQU-ART-013, AET-AQU-ART-014, AET-AQU-ART-015, AET-AQU-ART-016, AET-AQU-ART-017, AET-AQU-ART-018, AET-AQU-ART-019 (+335 további)
- `faj_kaszt_hiba`: 41 tétel. Példák: AET-AQU-ART-004, AET-AQU-ART-006, AET-AQU-ART-009, AET-AQU-ART-011, AET-AQU-ART-012, AET-AQU-ART-013, AET-AQU-ART-017, AET-AQU-ART-021, AET-AQU-ART-024, AET-AQU-ART-029, AET-TER-DRU-007, AET-TER-DRU-008, AET-TER-DRU-010, AET-TER-DRU-012, AET-TER-DRU-018 (+26 további)
- `CORE01-többlet`: 2 tétel. Példák: AET-AQU-ART-032, AET-AQU-ART-047
- `kiadásfüggő átvezetés`: 2 tétel. Példák: AET-AQU-ART-032, AET-AQU-ART-047
- `terminológiai_hiba`: 283 tétel. Példák: AET-AQU-ART-049, AET-TER-DRU-002, AET-TER-DRU-010, AET-TER-DRU-012, AET-TER-DRU-021, AET-TER-DRU-026, AET-TER-DRU-027, AET-TER-DRU-030, AET-TER-DRU-031, AET-TER-DRU-032, AET-TER-DRU-040, AET-TER-DRU-049, AET-TER-DRU-055, AET-TER-WHU-001, AET-TER-WHU-002 (+268 további)
- `kulcsszó-használati_hiba`: 198 tétel. Példák: AET-TER-DRU-001, AET-TER-DRU-003, AET-TER-DRU-009, AET-TER-DRU-025, AET-TER-WHU-005, AET-LUX-FHL-002, AET-LUX-FHL-006, AET-LUX-FHL-007, AET-LUX-FHL-008, AET-LUX-FHL-010, AET-LUX-FHL-013, AET-LUX-FHL-018, AET-LUX-FHL-020, AET-LUX-FHL-021, AET-LUX-FHL-022 (+183 további)
- `Ősforrás-zónakezelési_hiba`: 1 tétel. Példák: AET-TER-DRU-039
- `státuszkonzisztencia_javítás`: 17 tétel. Példák: AET-LUX-FHL-009, AET-LUX-FHL-011, AET-LUX-FHL-012, AET-LUX-FHL-014, AET-LUX-FHL-019, AET-LUX-FHL-024, AET-LUX-FHL-026, AET-LUX-FHL-039, AET-LUX-FHL-042, AET-LUX-FHL-048, AET-LUX-FHL-054, AET-LUX-APJ-008, AET-LUX-APJ-019, AET-LUX-APJ-027, AET-LUX-APJ-028 (+2 további)
- `tesztelési_státusz`: 17 tétel. Példák: AET-LUX-FHL-009, AET-LUX-FHL-011, AET-LUX-FHL-012, AET-LUX-FHL-014, AET-LUX-FHL-019, AET-LUX-FHL-024, AET-LUX-FHL-026, AET-LUX-FHL-039, AET-LUX-FHL-042, AET-LUX-FHL-048, AET-LUX-FHL-054, AET-LUX-APJ-008, AET-LUX-APJ-019, AET-LUX-APJ-027, AET-LUX-APJ-028 (+2 további)
- `identitásütközés`: 2 tétel. Példák: AET-UMB-ARS-001, AET-UMB-ARS-017
- `laptípusnyelv_hiba`: 11 tétel. Példák: AET-UMB-ARS-002, AET-UMB-ARS-005, AET-UMB-ARS-008, AET-UMB-ARS-009, AET-UMB-ARS-012, AET-UMB-ARS-013, AET-UMB-ARS-014, AET-UMB-ARS-021, AET-UMB-ARS-028, AET-UMB-ARS-035, AET-UMB-ARS-039
- `szabályszöveg_pontosítás`: 6 tétel. Példák: AET-UMB-ARS-002, AET-UMB-ARS-004, AET-UMB-ARS-007, AET-UMB-ARS-009, AET-UMB-ARS-017, AET-UMB-ARS-031
- `rejtett_információ`: 2 tétel. Példák: AET-UMB-ARS-005, AET-UMB-ARS-040
- `erőforrásnyelv_hiba`: 2 tétel. Példák: AET-UMB-ARS-006, AET-UMB-ARS-027
- `zónanyelv_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-007
- `lock_gyanú`: 2 tétel. Példák: AET-UMB-ARS-009, AET-UMB-ARS-029
- `időtartam_pontosítás`: 4 tétel. Példák: AET-UMB-ARS-010, AET-UMB-ARS-046, AET-UMB-LEA-028, AET-VEN-VIH-022
- `rejtett_jel_feltétel`: 1 tétel. Példák: AET-UMB-ARS-010
- `költségnövelés_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-011
- `tempó-lock_gyanú`: 1 tétel. Példák: AET-UMB-ARS-011
- `erőforrás-loop_gyanú`: 1 tétel. Példák: AET-UMB-ARS-012
- `ismételhető_sebzés_gyanú`: 1 tétel. Példák: AET-UMB-ARS-013
- `tutor_túlstabilitás`: 2 tétel. Példák: AET-UMB-ARS-014, AET-UMB-ARS-015
- `önmentés_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-014
- `Üresség-nyelv`: 3 tétel. Példák: AET-UMB-ARS-015, AET-UMB-ARS-020, AET-UMB-ARS-042
- `Hős_engine_gyanú`: 1 tétel. Példák: AET-UMB-ARS-015
- `információelőny`: 3 tétel. Példák: AET-UMB-ARS-016, AET-UMB-ARS-026, AET-UMB-ARS-032
- `discard-trigger_kivezetés`: 1 tétel. Példák: AET-UMB-ARS-017
- `névprofil_későbbi_figyelés`: 1 tétel. Példák: AET-UMB-ARS-019
- `saját_kézszűrés_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-020
- `húzó_engine_gyanú`: 3 tétel. Példák: AET-UMB-ARS-021, AET-UMB-ARS-040, AET-UMB-LEA-022
- `célzásvédelem_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-022
- `trigger_mező_eltérés`: 1 tétel. Példák: AET-UMB-ARS-024
- `fázisnyelv_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-024
- `ismétlődő_húzás_gyanú`: 1 tétel. Példák: AET-UMB-ARS-025
- `tempó-kontroll`: 1 tétel. Példák: AET-UMB-ARS-025
- `EXUL-elhatárolás`: 5 tétel. Példák: AET-UMB-ARS-026, AET-UMB-ARS-044, AET-UMB-ARS-052, AET-UMB-ARS-057, AET-UMB-LEA-008
- `paklipusztítás_visszafogása`: 1 tétel. Példák: AET-UMB-ARS-026
- `ideiglenes_aura_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-027
- `Jel-trigger`: 1 tétel. Példák: AET-UMB-ARS-028
- `burst_gyanú`: 1 tétel. Példák: AET-UMB-ARS-028
- `globális_költségnövelés`: 1 tétel. Példák: AET-UMB-ARS-029
- `Rezonancia_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-029
- `ingyenes_aktiválás`: 1 tétel. Példák: AET-UMB-ARS-030
- `feltételmegkerülés`: 1 tétel. Példák: AET-UMB-ARS-030
- `Jel-engine_lock_gyanú`: 1 tétel. Példák: AET-UMB-ARS-030
- `Reakció_nyelv`: 6 tétel. Példák: AET-UMB-ARS-031, AET-UMB-ARS-033, AET-UMB-ARS-051, AET-UMB-LEA-031, AET-UMB-LEA-032, AET-UMB-LEA-035
- `Burst_törlés`: 4 tétel. Példák: AET-UMB-ARS-031, AET-UMB-ARS-033, AET-UMB-LEA-031, AET-UMB-LEA-035
- `tempómanipuláció`: 1 tétel. Példák: AET-UMB-ARS-032
- `sebzés_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-033
- `szövegtisztítás`: 1 tétel. Példák: AET-UMB-ARS-034
- `paklitetej_manipuláció`: 1 tétel. Példák: AET-UMB-ARS-034
- `Jel_pozíciómanipuláció`: 1 tétel. Példák: AET-UMB-ARS-035
- `free_cast_loop_gyanú`: 1 tétel. Példák: AET-UMB-ARS-037
- `Riadó_loop_gyanú`: 1 tétel. Példák: AET-UMB-ARS-037
- `költségcsökkentés_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-037
- `varázslat_nyelv_hiba`: 2 tétel. Példák: AET-UMB-ARS-038, AET-UMB-ARS-049
- `pozíciós_mentés`: 1 tétel. Példák: AET-UMB-ARS-038
- `célzásreakció`: 1 tétel. Példák: AET-UMB-ARS-038
- `tempo_gyanú`: 2 tétel. Példák: AET-UMB-ARS-038, AET-UMB-ARS-049
- `tutor_engine_gyanú`: 1 tétel. Példák: AET-UMB-ARS-039
- `aktiválási_tilalom`: 1 tétel. Példák: AET-UMB-ARS-039
- `túl_tág_immunitás`: 1 tétel. Példák: AET-UMB-ARS-041
- `Ige_Rituálé_nyelv_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-041
- `célzásvédelem`: 2 tétel. Példák: AET-UMB-ARS-041, AET-VEN-EGU-051
- `kézrombolás`: 1 tétel. Példák: AET-UMB-ARS-042
- `választásos_kényszerítés`: 1 tétel. Példák: AET-UMB-ARS-042
- `Aura_fizetés_nyelv`: 1 tétel. Példák: AET-UMB-ARS-043
- `késleltetett_eltávolítás`: 1 tétel. Példák: AET-UMB-ARS-043
- `Ősforrás_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-043
- `random_discard_visszafogás`: 2 tétel. Példák: AET-UMB-ARS-044, AET-UMB-LEA-008
- `kézinformáció`: 1 tétel. Példák: AET-UMB-ARS-044
- `Jel-szinergia`: 1 tétel. Példák: AET-UMB-ARS-044
- `célzott_kézrombolás`: 1 tétel. Példák: AET-UMB-ARS-045
- `laptípusnyelv`: 1 tétel. Példák: AET-UMB-ARS-045
- `kontrollváltás`: 1 tétel. Példák: AET-UMB-ARS-046
- `Jel_formátum`: 20 tétel. Példák: AET-UMB-ARS-047, AET-UMB-ARS-048, AET-UMB-LEA-047, AET-UMB-LEA-052, AET-VEN-VIH-047, AET-VEN-VIH-048, AET-VEN-VIH-049, AET-VEN-VIH-050, AET-VEN-VIH-051, AET-VEN-VIH-052, AET-VEN-VIH-053, AET-VEN-VIH-054, AET-VEN-EGU-047, AET-VEN-EGU-048, AET-VEN-EGU-049 (+5 további)
- `célpontátirányítás`: 1 tétel. Példák: AET-UMB-ARS-047
- `szabályos_célpont_pontosítás`: 2 tétel. Példák: AET-UMB-ARS-047, AET-UMB-ARS-054
- `kulcsszóvesztés`: 2 tétel. Példák: AET-UMB-ARS-048, AET-UMB-LEA-035
- `idézésbüntetés`: 1 tétel. Példák: AET-UMB-ARS-048
- `adóztató_counter`: 1 tétel. Példák: AET-UMB-ARS-049
- `költségbizonytalanság`: 1 tétel. Példák: AET-UMB-ARS-049
- `Pecsét_támadás_reakció`: 1 tétel. Példák: AET-UMB-ARS-050
- `saját_áldozat`: 1 tétel. Példák: AET-UMB-ARS-050
- `célpontfeltétel_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-050
- `Burst_pontosítás`: 2 tétel. Példák: AET-UMB-ARS-051, AET-VEN-VIH-036
- `structured_mező_javítás`: 1 tétel. Példák: AET-UMB-ARS-051
- `Ősforrás_büntetés_visszafogás`: 1 tétel. Példák: AET-UMB-ARS-051
- `ellenkontroll_gyanú`: 1 tétel. Példák: AET-UMB-ARS-051
- `extra_húzás_büntetés`: 1 tétel. Példák: AET-UMB-ARS-052
- `kézrombolás_visszafogás`: 1 tétel. Példák: AET-UMB-ARS-052
- `Pecsétsebzés`: 2 tétel. Példák: AET-UMB-ARS-052, AET-VEN-EGU-058
- `támadásreakció`: 1 tétel. Példák: AET-UMB-ARS-053
- `paklialjra_helyezés`: 1 tétel. Példák: AET-UMB-ARS-053
- `tempo_removal`: 1 tétel. Példák: AET-UMB-ARS-053
- `Riadó_átirányítás`: 1 tétel. Példák: AET-UMB-ARS-054
- `túl_homályos_hatás`: 1 tétel. Példák: AET-UMB-ARS-054
- `minimumköltség_pontosítás`: 1 tétel. Példák: AET-UMB-ARS-055
- `kaszt_engine_gyanú`: 1 tétel. Példák: AET-UMB-ARS-055
- `Üresség_nyelv`: 9 tétel. Példák: AET-UMB-ARS-056, AET-UMB-LEA-001, AET-UMB-LEA-002, AET-UMB-LEA-004, AET-UMB-LEA-006, AET-UMB-LEA-015, AET-UMB-LEA-032, AET-UMB-LEA-041, AET-UMB-LEA-055
- `saját_paklitetej_szűrés`: 1 tétel. Példák: AET-UMB-ARS-056
- `graveyard_törlés`: 1 tétel. Példák: AET-UMB-ARS-056
- `discard-trigger`: 1 tétel. Példák: AET-UMB-ARS-057
- `sebző_engine_gyanú`: 1 tétel. Példák: AET-UMB-ARS-057
- `Jel-húzó_engine`: 1 tétel. Példák: AET-UMB-ARS-058
- `Aura_nyelv_hiba`: 1 tétel. Példák: AET-UMB-ARS-058
- `túl_sok_ismétlődő_érték`: 1 tétel. Példák: AET-UMB-ARS-058
- `Visszhang_pontosítás`: 5 tétel. Példák: AET-UMB-LEA-001, AET-UMB-LEA-002, AET-UMB-LEA-016, AET-UMB-LEA-020, AET-VEN-EGU-015
- `olcsó_húzó_engine`: 1 tétel. Példák: AET-UMB-LEA-001
- `célpontválasztás`: 1 tétel. Példák: AET-UMB-LEA-002
- `Főfaj_terminológia`: 1 tétel. Példák: AET-UMB-LEA-003
- `sacrifice_draw_engine`: 2 tétel. Példák: AET-UMB-LEA-003, AET-UMB-LEA-039
- `fázisnyelv`: 1 tétel. Példák: AET-UMB-LEA-003
- `késleltetett_visszatérés`: 2 tétel. Példák: AET-UMB-LEA-004, AET-UMB-LEA-006
- `Áramlat_pontosítás`: 1 tétel. Példák: AET-UMB-LEA-005
- `sacrifice_resource_engine`: 3 tétel. Példák: AET-UMB-LEA-005, AET-UMB-LEA-012, AET-UMB-LEA-034
- `ideiglenes_Aura`: 2 tétel. Példák: AET-UMB-LEA-005, AET-UMB-LEA-012
- `Kimerült_állapot`: 5 tétel. Példák: AET-UMB-LEA-006, AET-UMB-LEA-024, AET-UMB-LEA-045, AET-UMB-LEA-050, AET-UMB-LEA-056
- `önmegsemmisítés`: 1 tétel. Példák: AET-UMB-LEA-007
- `fázisnyelv_tisztítás`: 1 tétel. Példák: AET-UMB-LEA-007
- `Üresség-szinergia`: 2 tétel. Példák: AET-UMB-LEA-008, AET-UMB-LEA-034
- `választásos_zsarolás`: 1 tétel. Példák: AET-UMB-LEA-008
- `duplikált_szöveg`: 1 tétel. Példák: AET-UMB-LEA-009
- `halálhelyettesítés`: 1 tétel. Példák: AET-UMB-LEA-009
- `sacrifice_engine`: 2 tétel. Példák: AET-UMB-LEA-009, AET-UMB-LEA-011
- `permanens_ATK`: 1 tétel. Példák: AET-UMB-LEA-009
- `Üresség-trigger`: 3 tétel. Példák: AET-UMB-LEA-010, AET-UMB-LEA-025, AET-UMB-LEA-038
- `permanens_HP_engine`: 2 tétel. Példák: AET-UMB-LEA-010, AET-UMB-LEA-055
- `permanens_statnövekedés`: 1 tétel. Példák: AET-UMB-LEA-011
- `Riadó_nyelv`: 1 tétel. Példák: AET-UMB-LEA-012
- `támadási_költség`: 1 tétel. Példák: AET-UMB-LEA-013
- `sacrifice`: 1 tétel. Példák: AET-UMB-LEA-013
- `ideiglenes_ATK`: 1 tétel. Példák: AET-UMB-LEA-013
- `tetszőleges_sacrifice_visszafogás`: 1 tétel. Példák: AET-UMB-LEA-014
- `random_sebzés_törlés`: 1 tétel. Példák: AET-UMB-LEA-014
- `finisher_engine_gyanú`: 1 tétel. Példák: AET-UMB-LEA-014
- `self_mill`: 1 tétel. Példák: AET-UMB-LEA-015
- `permanens_HP`: 1 tétel. Példák: AET-UMB-LEA-015
- `permanens_ATK_buff`: 1 tétel. Példák: AET-UMB-LEA-016
- `tiszta_keyword_lap`: 3 tétel. Példák: AET-UMB-LEA-017, AET-UMB-LEA-019, AET-UMB-LEA-021
- `sebzés_trigger_pontosítás`: 1 tétel. Példák: AET-UMB-LEA-018
- `Aeternal_gyógyítás`: 3 tétel. Példák: AET-UMB-LEA-018, AET-UMB-LEA-027, AET-UMB-LEA-033
- `ideiglenes_ATK_debuff`: 1 tétel. Példák: AET-UMB-LEA-020
- `Harmonizálás_értékhiány`: 1 tétel. Példák: AET-UMB-LEA-022
- `támogatott_Entitás_haláltrigger`: 1 tétel. Példák: AET-UMB-LEA-022
- `Ürességből_visszatérés`: 1 tétel. Példák: AET-UMB-LEA-023
- `kulcsszóadás_időtartam`: 1 tétel. Példák: AET-UMB-LEA-023
- `graveyard_nyelv_hiba`: 1 tétel. Példák: AET-UMB-LEA-023
- `ismétlődő_feltámasztás`: 1 tétel. Példák: AET-UMB-LEA-024
- `fázistrigger_hiba`: 1 tétel. Példák: AET-UMB-LEA-024
- `loop_gyanú`: 2 tétel. Példák: AET-UMB-LEA-024, AET-UMB-LEA-043
- `tömeges_Horizont-sebzés`: 1 tétel. Példák: AET-UMB-LEA-025
- `zónanyelv_tisztítás`: 1 tétel. Példák: AET-UMB-LEA-025
- `sacrifice-trigger`: 1 tétel. Példák: AET-UMB-LEA-026
- `permanens_ATK_snowball`: 1 tétel. Példák: AET-UMB-LEA-026
- `structured_trigger_hiba`: 1 tétel. Példák: AET-UMB-LEA-026
- `harci_ölés_trigger`: 1 tétel. Példák: AET-UMB-LEA-027
- `feltételes_combat_buff`: 1 tétel. Példák: AET-UMB-LEA-028
- `Visszhang_visszatérés`: 1 tétel. Példák: AET-UMB-LEA-029
- `nagytest_recursion`: 2 tétel. Példák: AET-UMB-LEA-029, AET-UMB-LEA-036
- `max_HP_felezés`: 1 tétel. Példák: AET-UMB-LEA-029
- `Kimerült_Zenit`: 3 tétel. Példák: AET-UMB-LEA-029, AET-UMB-LEA-036, AET-UMB-LEA-043
- `Hős_finisher`: 1 tétel. Példák: AET-UMB-LEA-030
- `tömeges_Magnitúdó-szűrt_pusztítás`: 1 tétel. Példák: AET-UMB-LEA-030
- `Visszhang_szinergia`: 1 tétel. Példák: AET-UMB-LEA-030
- `board_wipe_gyanú`: 1 tétel. Példák: AET-UMB-LEA-030
- `sacrifice_removal`: 1 tétel. Példák: AET-UMB-LEA-031
- `célzott_eltávolítás`: 2 tétel. Példák: AET-UMB-LEA-031, AET-UMB-LEA-037
- `kézbe_visszavétel`: 1 tétel. Példák: AET-UMB-LEA-032
- `graveyard_canonical_hiba`: 2 tétel. Példák: AET-UMB-LEA-032, AET-UMB-LEA-041
- `nyelvtani_javítás`: 2 tétel. Példák: AET-UMB-LEA-033, AET-UMB-LEA-046
- `Pecsét_gyógyítás_pontosítás`: 1 tétel. Példák: AET-UMB-LEA-033
- `változó_Aura`: 1 tétel. Példák: AET-UMB-LEA-034
- `felső_limit`: 2 tétel. Példák: AET-UMB-LEA-034, AET-UMB-LEA-038
- `ability_lock_címke`: 1 tétel. Példák: AET-UMB-LEA-035
- `korlátlan_feltámasztás`: 1 tétel. Példák: AET-UMB-LEA-036
- `Aktív_állapot_visszafogás`: 1 tétel. Példák: AET-UMB-LEA-036
- `pusztítás_vs_feláldozás`: 1 tétel. Példák: AET-UMB-LEA-037
- `Horizont-költség`: 1 tétel. Példák: AET-UMB-LEA-037
- `halálszámlálás`: 1 tétel. Példák: AET-UMB-LEA-038
- `változó_sebzés`: 1 tétel. Példák: AET-UMB-LEA-038
- `túl_olcsó_2_lapos_húzás`: 1 tétel. Példák: AET-UMB-LEA-039
- `Fajszűrés`: 1 tétel. Példák: AET-UMB-LEA-039
- `Fajszűrt_húzás`: 1 tétel. Példák: AET-UMB-LEA-040
- `maximum_3`: 1 tétel. Példák: AET-UMB-LEA-040
- `Domínium_nyelv`: 1 tétel. Példák: AET-UMB-LEA-040
- `self_mill_tutor`: 1 tétel. Példák: AET-UMB-LEA-041
- `kétoldali_Horizont-sebzés`: 1 tétel. Példák: AET-UMB-LEA-042
- `saját_halálból_húzás`: 1 tétel. Példák: AET-UMB-LEA-042
- `húzó_engine_pontosítás`: 1 tétel. Példák: AET-UMB-LEA-042
- `többcélpontos_recursion`: 1 tétel. Példák: AET-UMB-LEA-043
- `Domínium_mező_pontosítás`: 1 tétel. Példák: AET-UMB-LEA-043
- `Oltalom_megkerülés_törlés`: 1 tétel. Példák: AET-UMB-LEA-044
- `nem_célzó_áldoztatás`: 1 tétel. Példák: AET-UMB-LEA-044
- `célzott_pusztítás_visszafogás`: 1 tétel. Példák: AET-UMB-LEA-044
- `temető_nyelv_hiba`: 1 tétel. Példák: AET-UMB-LEA-045
- `recursion`: 1 tétel. Példák: AET-UMB-LEA-045
- `LEA-036_funkcióközelség`: 1 tétel. Példák: AET-UMB-LEA-045
- `Üresség-számolás`: 1 tétel. Példák: AET-UMB-LEA-046
- `sebzésmaximum`: 1 tétel. Példák: AET-UMB-LEA-046
- `harci_haláltrigger`: 1 tétel. Példák: AET-UMB-LEA-047
- `hangulati_szöveg_törlés`: 1 tétel. Példák: AET-UMB-LEA-047
- `Rituálé-counter`: 2 tétel. Példák: AET-UMB-LEA-048, AET-UMB-LEA-053
- `saját_Zenit-áldozat`: 2 tétel. Példák: AET-UMB-LEA-048, AET-UMB-LEA-049
- `varázslatnyelv_törlés`: 1 tétel. Példák: AET-UMB-LEA-048
- `summon-punish`: 1 tétel. Példák: AET-UMB-LEA-049
- `nagy_Entitás_eltávolítás`: 1 tétel. Példák: AET-UMB-LEA-049
- `aktiválási_feltétel`: 1 tétel. Példák: AET-UMB-LEA-049
- `Token-rendszer`: 2 tétel. Példák: AET-UMB-LEA-050, AET-UMB-LEA-056
- `Horizont_mező`: 1 tétel. Példák: AET-UMB-LEA-050
- `névaudit_később`: 1 tétel. Példák: AET-UMB-LEA-050
- `támadásbüntetés`: 1 tétel. Példák: AET-UMB-LEA-051
- `Métely_időtartam`: 1 tétel. Példák: AET-UMB-LEA-051
- `Pecséttörés-trigger`: 1 tétel. Példák: AET-UMB-LEA-052
- `tömeges_megtorló_sebzés`: 1 tétel. Példák: AET-UMB-LEA-052
- `saját_Horizont-áldozat`: 1 tétel. Példák: AET-UMB-LEA-053
- `Aeternal-sebzés`: 1 tétel. Példák: AET-UMB-LEA-053
- `LEA-048_duplikáció`: 1 tétel. Példák: AET-UMB-LEA-053
- `halálos_harci_sebzés`: 1 tétel. Példák: AET-UMB-LEA-054
- `combat_trade`: 1 tétel. Példák: AET-UMB-LEA-054
- `Üresség-hangulat_törlés`: 1 tétel. Példák: AET-UMB-LEA-054
- `Sík_recursion-buff`: 1 tétel. Példák: AET-UMB-LEA-055
- `körönkénti_limit`: 2 tétel. Példák: AET-UMB-LEA-055, AET-UMB-LEA-057
- `Horizont-mező`: 1 tétel. Példák: AET-UMB-LEA-056
- `death_check`: 1 tétel. Példák: AET-UMB-LEA-056
- `sacrifice-erőforrás_engine`: 1 tétel. Példák: AET-UMB-LEA-057
- `UMBRA_Aura_nyelv`: 1 tétel. Példák: AET-UMB-LEA-057
- `trigger_pontosítás`: 2 tétel. Példák: AET-UMB-LEA-057, AET-VEN-EGU-026
- `kétoldali_sacrifice_Sík`: 1 tétel. Példák: AET-UMB-LEA-058
- `Beáramlás_fázis`: 1 tétel. Példák: AET-UMB-LEA-058
- `húzáskompenzáció`: 1 tétel. Példák: AET-UMB-LEA-058
- `aszimmetrikus_engine_gyanú`: 1 tétel. Példák: AET-UMB-LEA-058
- `structured_trigger_hiány`: 4 tétel. Példák: AET-VEN-VIH-011, AET-VEN-VIH-013, AET-VEN-VIH-023, AET-VEN-VIH-029
- `random_célpont`: 1 tétel. Példák: AET-VEN-VIH-013
- `erőforrás_gyanú`: 1 tétel. Példák: AET-VEN-VIH-022
- `Surge_interakció`: 1 tétel. Példák: AET-VEN-VIH-025
- `structured_hatáscímke_hiány`: 6 tétel. Példák: AET-VEN-VIH-026, AET-VEN-VIH-040, AET-VEN-VIH-042, AET-VEN-VIH-044, AET-VEN-EGU-024, AET-VEN-EGU-035
- `célpont_meghatározás_pontosítva`: 2 tétel. Példák: AET-VEN-VIH-028, AET-VEN-EGU-008
- `structured_trigger_bővítés`: 3 tétel. Példák: AET-VEN-VIH-028, AET-VEN-EGU-051, AET-VEN-EGU-053
- `lane_interakció`: 1 tétel. Példák: AET-VEN-VIH-038
- `turn_tracking`: 1 tétel. Példák: AET-VEN-VIH-041
- `token_zóna_pontosítás`: 1 tétel. Példák: AET-VEN-VIH-043
- `trigger_duplikálás`: 1 tétel. Példák: AET-VEN-VIH-044
- `Visszaállítás_korlát_pontosítás`: 1 tétel. Példák: AET-VEN-VIH-045
- `extra_betörés_fázis`: 1 tétel. Példák: AET-VEN-VIH-046
- `attack_nullify`: 4 tétel. Példák: AET-VEN-VIH-047, AET-VEN-EGU-037, AET-VEN-EGU-052, AET-VEN-EGU-054
- `choice_hatás`: 1 tétel. Példák: AET-VEN-VIH-048
- `harci_interakció`: 2 tétel. Példák: AET-VEN-VIH-050, AET-VEN-EGU-011
- `attack_precombat_damage`: 1 tétel. Példák: AET-VEN-VIH-051
- `hatásfeldolgozási_sorrend`: 1 tétel. Példák: AET-VEN-VIH-052
- `Pecsét_rendszer_korrekció`: 1 tétel. Példák: AET-VEN-VIH-053
- `seal_break_prevention`: 1 tétel. Példák: AET-VEN-VIH-053
- `deck_bottom`: 1 tétel. Példák: AET-VEN-VIH-053
- `free_cast_summon`: 1 tétel. Példák: AET-VEN-VIH-054
- `Sík_globális_pontosítás`: 4 tétel. Példák: AET-VEN-VIH-055, AET-VEN-VIH-056, AET-VEN-VIH-057, AET-VEN-VIH-058
- `szomszédosság`: 1 tétel. Példák: AET-VEN-VIH-055
- `Visszaállítás_trigger`: 1 tétel. Példák: AET-VEN-VIH-057
- `kettős_síkhatás`: 1 tétel. Példák: AET-VEN-VIH-058
- `Visszhang_recursion`: 1 tétel. Példák: AET-VEN-EGU-001
- `block_restrict`: 2 tétel. Példák: AET-VEN-EGU-002, AET-VEN-EGU-027
- `Pecsét_trigger_pontosítás`: 1 tétel. Példák: AET-VEN-EGU-010
- `visszaküldés_trigger`: 1 tétel. Példák: AET-VEN-EGU-012
- `tömeges_visszaküldés`: 4 tétel. Példák: AET-VEN-EGU-013, AET-VEN-EGU-014, AET-VEN-EGU-030, AET-VEN-EGU-046
- `információs_hatás`: 1 tétel. Példák: AET-VEN-EGU-016
- `célpontvédelem`: 1 tétel. Példák: AET-VEN-EGU-019
- `ön_visszavétel`: 2 tétel. Példák: AET-VEN-EGU-020, AET-VEN-EGU-053
- `counterspell`: 2 tétel. Példák: AET-VEN-EGU-020, AET-VEN-EGU-051
- `conditional_draw`: 1 tétel. Példák: AET-VEN-EGU-022
- `reveal`: 2 tétel. Példák: AET-VEN-EGU-022, AET-VEN-EGU-049
- `structured_mező_javítva`: 1 tétel. Példák: AET-VEN-EGU-023
- `erőforrás_csökkentés`: 1 tétel. Példák: AET-VEN-EGU-023
- `kulcsszó_eltávolítás`: 1 tétel. Példák: AET-VEN-EGU-024
- `aktivált_képesség`: 1 tétel. Példák: AET-VEN-EGU-026
- `visszaküldés`: 5 tétel. Példák: AET-VEN-EGU-026, AET-VEN-EGU-033, AET-VEN-EGU-048, AET-VEN-EGU-052, AET-VEN-EGU-054
- `Légies_Oltalom_kombó`: 1 tétel. Példák: AET-VEN-EGU-028
- `discard`: 3 tétel. Példák: AET-VEN-EGU-029, AET-VEN-EGU-049, AET-VEN-EGU-050
- `identitás_elhatárolás`: 2 tétel. Példák: AET-VEN-EGU-029, AET-VEN-EGU-050
- `szimmetrikus_hatás`: 2 tétel. Példák: AET-VEN-EGU-030, AET-VEN-EGU-046
- `bounce_szinergia`: 1 tétel. Példák: AET-VEN-EGU-032
- `kompenzációs_húzás`: 1 tétel. Példák: AET-VEN-EGU-033
- `pozíciócsere`: 1 tétel. Példák: AET-VEN-EGU-034
- `kontrolloldal_kérdés`: 1 tétel. Példák: AET-VEN-EGU-034
- `időtartam_hiány`: 1 tétel. Példák: AET-VEN-EGU-035
- `keyword_eltávolítás`: 1 tétel. Példák: AET-VEN-EGU-035
- `sebzés`: 1 tétel. Példák: AET-VEN-EGU-035
- `Burst_védekezés`: 1 tétel. Példák: AET-VEN-EGU-037
- `Áramlat_pozíció`: 2 tétel. Példák: AET-VEN-EGU-038, AET-VEN-EGU-046
- `feltételes_mozgatás`: 1 tétel. Példák: AET-VEN-EGU-038
- `bounce_fallback`: 1 tétel. Példák: AET-VEN-EGU-038
- `szimmetrikus_visszaküldés`: 1 tétel. Példák: AET-VEN-EGU-039
- `választási_sorrend`: 1 tétel. Példák: AET-VEN-EGU-039
- `tömeges_keyword_adás`: 1 tétel. Példák: AET-VEN-EGU-040
- `tömeges_sebzés`: 1 tétel. Példák: AET-VEN-EGU-041
- `keyword_szűrés`: 1 tétel. Példák: AET-VEN-EGU-041
- `extra_támadás`: 1 tétel. Példák: AET-VEN-EGU-042
- `ready_prevention`: 1 tétel. Példák: AET-VEN-EGU-042
- `Üresség_pontosítás`: 1 tétel. Példák: AET-VEN-EGU-043
- `kompenzációs_megidézés`: 1 tétel. Példák: AET-VEN-EGU-043
- `topdeck_summon`: 1 tétel. Példák: AET-VEN-EGU-043
- `változó_számú_visszavétel`: 1 tétel. Példák: AET-VEN-EGU-044
- `Jel_pusztítás`: 1 tétel. Példák: AET-VEN-EGU-044
- `többcélpontos_visszaküldés`: 1 tétel. Példák: AET-VEN-EGU-045
- `sebzésmegelőzés`: 1 tétel. Példák: AET-VEN-EGU-047
- `exhaust`: 1 tétel. Példák: AET-VEN-EGU-047
- `summon_punish`: 1 tétel. Példák: AET-VEN-EGU-048
- `draw_intercept`: 1 tétel. Példák: AET-VEN-EGU-049
- `opcionális_húzás`: 1 tétel. Példák: AET-VEN-EGU-053
- `Pecsét_támadás`: 1 tétel. Példák: AET-VEN-EGU-054
- `Sík_hatás`: 4 tétel. Példák: AET-VEN-EGU-055, AET-VEN-EGU-056, AET-VEN-EGU-057, AET-VEN-EGU-058
- `bounce_trigger`: 2 tétel. Példák: AET-VEN-EGU-055, AET-VEN-EGU-058
- `tömeges_buff`: 1 tétel. Példák: AET-VEN-EGU-055
- `resource_gain`: 1 tétel. Példák: AET-VEN-EGU-056
- `ideiglenes_aura`: 1 tétel. Példák: AET-VEN-EGU-056
- `célzási_költség`: 1 tétel. Példák: AET-VEN-EGU-057
- `névütközés_gyanú`: 1 tétel. Példák: AET-AET-FGS-040

### 11. [P2] CARD_PRINTINGS – eltérés a CARDS_MASTER print mezőitől

Összesen: 2 tétel.

- AET-IGN-HAM-023 | Play_Legal_Status | CORE01_needs_token_rules | CORE01_test_required
- AET-IGN-HAM-031 | Play_Legal_Status | CORE01_needs_token_rules | CORE01_test_required

### 12. [P2] DECISION_LOG – üres mezők

Összesen: 3 tétel.

- 1 | D-CORE01-TOKEN-001 | ['Megjegyzés']
- 2 | D-CARDTEXT-SIGN-001 | ['Megjegyzés']
- 3 | D-PLANE-001 | ['Megjegyzés']

### 13. [P2] NAME_PROFILE – fontos névprofil mező hiányzik

Összesen: 1 tétel.

- AET-UMB-LEA-037 | Erőszakos Végzet | ['Névforma']

### 14. [P2] PRODUCTS – Product_ID none / üres sor

Összesen: 5 tétel.

- 18
- 19
- 20
- 21
- 22

### 15. [P2] PRODUCT_DECKLISTS – Kártya_Név eltér a CARDS_MASTER aktuális névtől

Összesen: 28 tétel.

- TEST-CORE01-UMBRA | DECK-UMB-ARS-TEST-001 | AET-UMB-ARS-008 | Szindikátusi Jelmester | Szindikátusi Csapdamester
- TEST-CORE01-UMBRA | DECK-UMB-ARS-TEST-001 | AET-UMB-ARS-009 | Árnyközvetítő | Árnyék-közvetítő
- TEST-CORE01-UMBRA | DECK-UMB-ARS-TEST-001 | AET-UMB-ARS-015 | Noctis, az Árnyak Ura | Noctis az Árnyak Ura
- TEST-CORE01-UMBRA | DECK-UMB-ARS-TEST-001 | AET-UMB-ARS-032 | Kiszivárgott Titkok | Információszivárogtatás
- TEST-CORE01-UMBRA | DECK-UMB-ARS-TEST-001 | AET-UMB-ARS-037 | Árnylépés | Árnyék-Ugrás
- TEST-CORE01-UMBRA | DECK-UMB-ARS-TEST-001 | AET-UMB-ARS-039 | Alvilági Összeköttetések | Alvilági Kapcsolatok
- TEST-CORE01-UMBRA | DECK-UMB-ARS-TEST-001 | AET-UMB-ARS-049 | Váratlan Sarckivetés | Váratlan Adóellenőrzés
- TEST-CORE01-UMBRA | DECK-UMB-LEA-TEST-001 | AET-UMB-LEA-003 | Sírnyitó Tanítvány | Nekromanta Tanítvány
- TEST-CORE01-UMBRA | DECK-UMB-LEA-TEST-001 | AET-UMB-LEA-005 | Morvessa, a Lélekszívó Papnő | Lélekszívó Papnő
- TEST-CORE01-UMBRA | DECK-UMB-LEA-TEST-001 | AET-UMB-LEA-006 | Feltámadt Csontzúzó | Feltámadt Csonttörő
- TEST-CORE01-UMBRA | DECK-UMB-LEA-TEST-001 | AET-UMB-LEA-015 | Sírvermi Sírásó | Temetői Sírásó
- TEST-CORE01-UMBRA | DECK-UMB-LEA-TEST-001 | AET-UMB-LEA-024 | Elyrion, a Lelkek Pásztora | Lelkek Pásztora
- TEST-CORE01-UMBRA | DECK-UMB-LEA-TEST-001 | AET-UMB-LEA-030 | Azaroth, a Kaszás | Azaroth a Kaszás
- TEST-CORE01-UMBRA | DECK-UMB-LEA-TEST-001 | AET-UMB-LEA-036 | Ürességből Visszahívás | Visszahívás az Ürességből
- TEST-CORE01-UMBRA | DECK-UMB-LEA-TEST-001 | AET-UMB-LEA-050 | Sírkőcsapda | Sírkő-Csapda
- TEST-CORE01-UMBRA | DECK-UMB-LEA-TEST-001 | AET-UMB-LEA-056 | Csontok Szigete | Csontvázak Szigete
- TEST-CORE01-UMBRA | DECK-UMB-MIX-TEST-001 | AET-UMB-ARS-008 | Szindikátusi Jelmester | Szindikátusi Csapdamester
- TEST-CORE01-UMBRA | DECK-UMB-MIX-TEST-001 | AET-UMB-ARS-015 | Noctis, az Árnyak Ura | Noctis az Árnyak Ura
- TEST-CORE01-UMBRA | DECK-UMB-MIX-TEST-001 | AET-UMB-LEA-003 | Sírnyitó Tanítvány | Nekromanta Tanítvány
- TEST-CORE01-UMBRA | DECK-UMB-MIX-TEST-001 | AET-UMB-LEA-005 | Morvessa, a Lélekszívó Papnő | Lélekszívó Papnő
- TEST-CORE01-UMBRA | DECK-UMB-MIX-TEST-001 | AET-UMB-LEA-024 | Elyrion, a Lelkek Pásztora | Lelkek Pásztora
- TEST-CORE01-UMBRA | DECK-UMB-MIX-TEST-001 | AET-UMB-ARS-032 | Kiszivárgott Titkok | Információszivárogtatás
- TEST-CORE01-UMBRA | DECK-UMB-MIX-TEST-001 | AET-UMB-ARS-039 | Alvilági Összeköttetések | Alvilági Kapcsolatok
- TEST-CORE01-UMBRA | DECK-UMB-MIX-TEST-001 | AET-UMB-ARS-049 | Váratlan Sarckivetés | Váratlan Adóellenőrzés
- TEST-CORE01-UMBRA | DECK-UMB-MIX-TEST-001 | AET-UMB-LEA-050 | Sírkőcsapda | Sírkő-Csapda
- BKP-UMB01 | DECK-UMB-STARTER-001 | AET-UMB-LEA-006 | Feltámadt Csontzúzó | Feltámadt Csonttörő
- BKP-UMB01 | DECK-UMB-STARTER-001 | AET-UMB-LEA-017 | Csontpáncélos Harcos | Csontváz Harcos
- BKP-UMB01 | DECK-UMB-STARTER-001 | AET-UMB-LEA-018 | Vérszomjas Denevér | Vérszívó Denevér

### 16. [P3] AUDIT_LOG – Kártya név nem található pontosan CARDS_MASTER-ben (lehet összegző log)

Összesen: 42 tétel.

- AUD-IGN-HAM-JEL-001 | Forró Talaj; Robbanó Pajzs; Csapda a Füstben; Hamis Parancs; Tüzes Megtorlás; Lángoló Visszavágás; Csapda a Hamuban; Izzó Aura
- AUD-IGN-LAN-CLOSE-001 | Lángidéző klán
- AUD-IGN-HAM-CLOSE-001 | Hamvaskezű klán
- AUD-IGN-HAM-TOKEN-001 | Hamvaskezű Toborzó; Goblin Taktika
- AUD-IGN-DECISION-FIELD-001 | IGNIS döntésmező-tisztítás
- AUD-IGN-STRUCTURED-EXPORT-001 | IGNIS structured mezők és runtime-export
- AUD-IGN-NAMEPROFILE-001 | IGNIS névprofil első kör
- AUD-AQU-ART-CLOSE-001 | Áramlat-táncosok klán
- AUD-TER-DRU-CLOSE-001 | Ős-Druidák klán
- AUD-TER-WHU-CLOSE-001 | Vadon Vadászai klán
- AUD-LUX-FHL-CLOSE-001 | Fényhozó Lovagrend klánzárás
- AUD-LUX-APJ-KLANZARAS-20260609 | Aeterna Papjai klán
- AUD-LUX-BIR-STATUSZTISZTITAS-20260609 | LUX státusztisztítási csomag
- AUD-LUX-FHL-NAME-001 | Fényhozó Lovagrend névprofil
- AUD-LUX-APJ-NAME-001 | Aeterna Papjai névprofil
- AUD-LUX-NAME-RATIO-001 | LUX néveloszlási arány
- AUD-LUX-NAME-TERM-001 | LUX névterminológia
- AUD-UMB-ARS-001-010 | Árnyékszindikátus 001–010
- AUD-UMB-ARS-011-020 | Árnyékszindikátus 011–020
- AUD-UMB-ARS-021-030 | Árnyékszindikátus 021–030
- AUD-UMB-ARS-031-040 | Árnyékszindikátus 031–040
- AUD-UMB-ARS-041-050 | Árnyékszindikátus 041–050
- AUD-UMB-ARS-051-058 | Árnyékszindikátus 051–058
- AUD-UMB-ARS-TERMINOLOGY | Árnyékszindikátus terminológiai tisztítás
- AUD-UMB-ARS-STATUS | Árnyékszindikátus play legal státusz
- AUD-UMB-LEA-001-010 | Lélekaratók 001–010
- AUD-UMB-LEA-011-020 | Lélekaratók 011–020
- AUD-UMB-LEA-021-030 | Lélekaratók 021–030
- AUD-UMB-LEA-031-040 | Lélekaratók 031–040
- AUD-UMB-LEA-041-050 | Lélekaratók 041–050
- AUD-UMB-LEA-051-058 | Lélekaratók 051–058
- AUD-UMB-LEA-TERMINOLOGY | Lélekaratók terminológiai tisztítás
- AUD-UMB-LEA-STATUS | Lélekaratók play legal státusz
- AUD-VEN-VIH-STRUCT-001 | VENTUS / Viharhozók structured-bővítési jelöltek
- AUD-VEN-EGU-001 | VENTUS / Égbolt Úrai első CARDS_MASTER beemelés
- AUD-VEN-EGU-051-053-001 | Szétszéledő Köd; Váratlan Felszállás
- AUD-VEN-EGU-REVIEW-001 | VENTUS / Égbolt Úrai review státuszú lapok
- AUD-VEN-VIH-CLOSE-001 | VENTUS / Viharhozók klánzáró visszaellenőrzés
- AUD-VEN-CLOSE-001 | VENTUS közös klánzáró állapot
- AUD-AET-FGS-CLAN-001 | Fogaskerék Szövetség
- AUD-AET-KOB-CLAN-001 | Kóborlók
- AUD-AET-DECK-STARTER-001 | AETHER kezdőpakli-jelölt

### 17. [P3] CARDS_MASTER – Klán lapdarabszám eltér 58-tól (ha 58 a cél)

Összesen: 1 tétel.

- AQUA | Áramlat-táncosok | 60

### 18. [P3] CARDS_MASTER – canonical mezőkben régi / nem egységes angol engine kifejezések

- `counts`:
  - `graveyard`: 38
  - `spell`: 22
  - `spells`: 16
  - `board`: 1
- `examples`:
  - `graveyard`: [('AET-AQU-ART-060', 'Az Elveszett Áramlatok Csatornája', 'while this plane is active, once per turn when an allied AQUA entity leaves the Dominium to your hand or graveyard, gain 1 temporary AQUA aura this turn, then you may draw 1 card'), ('AET-LUX-APJ-002', 'Kegyhely-őrző Szerzetes', '[DOMINIUM] echo: when this entity goes to graveyard, choose 1 allied entity in your Dominium among your allied entities with the lowest current HP; it gains +2 max HP'), ('AET-LUX-APJ-003', 'Kóborló Lélek', '[DOMINIUM] ethereal; clarion: put the top card of your deck into your graveyard'), ('AET-LUX-APJ-008', 'Lélekidéző Főpapnő', '[ZENIT] harmonize 1; while this entity is in Zenit, if the supported allied Horizont entity in front in the same lane would take lethal damage, it survives at 1 HP and this entity goes to graveyard'), ('AET-LUX-APJ-010', 'Életadó Főpap', '[DOMINIUM] clarion: choose 1 entity with magnitude 2 or less in your graveyard; put it exhausted into an empty slot in your Dominium; this does not count as summoning'), ('AET-LUX-APJ-012', 'Könnyező Arkangyal', '[DOMINIUM] clarion: choose one - up to 2 allied entities in the Dominium gain +2 max HP; or put target allied entity with magnitude 3 or less from your graveyard exhausted into an empty Horizont slot in your Dominium, its abilities cannot activate until end of turn, this does not count as summoning'), ('AET-LUX-APJ-013', 'Aeterna Prófétája', '[DOMINIUM] echo: when this entity is destroyed and goes to graveyard, if you have a broken own seal, heal 2 HP from your Aeternal or your most damaged own seal'), ('AET-LUX-APJ-015', 'Temetői Koldus', '[DOMINIUM] echo: when this entity goes to graveyard, look at the top card of your deck; you may put that card into your graveyard'), ('AET-LUX-APJ-016', 'Hitbuzgó Zarándok', '[ZENIT] when an allied entity enters your Dominium from your graveyard by a card effect, this entity gains +1 ATK until end of match'), ('AET-LUX-APJ-018', 'Aeterna Diakónusa', '[ZENIT] harmonize 1; when the supported allied Horizont entity is destroyed and goes to graveyard, you may draw 1 card'), ('AET-LUX-APJ-019', 'Visszatért Mártír', '[DOMINIUM] if this entity enters your Dominium from your graveyard by an Incantation or Ritual effect, it gains celerity'), ('AET-LUX-APJ-020', 'Üresség-Kutató', '[DOMINIUM] clarion: look at the top 5 cards of your deck; you may choose 1 Incantation among them and put it into your graveyard; put the rest on the bottom of your deck in any order; then draw 1 card'), ('AET-LUX-APJ-024', 'Szent Ereklye Hordozója', '[ZENIT] resonance 1; while this entity is in Zenit, once per turn when you would play an Incantation or Ritual that puts an entity from your graveyard into your Dominium, it costs 1 less Aura, minimum 1; this cost reduction does not stack with other graveyard-to-Dominium Incantation or Ritual cost reductions'), ('AET-LUX-APJ-025', 'Angyali Hírnök', '[HORIZONT] ethereal; [DOMINIUM] clarion: you may put 1 card from your hand into your graveyard; if you do, gain 1 temporary LUX aura this turn'), ('AET-LUX-APJ-027', 'Feltámasztott Bajnok', '[HORIZONT] aegis; if this entity entered your Dominium from your graveyard by a card effect, it gains sundering and +2 ATK'), ('AET-LUX-APJ-029', 'Az Üresség Őre', '[DOMINIUM] ethereal; while this entity is in your Dominium, enemy Incantations, Rituals, and entity abilities cannot remove cards from your graveyard'), ('AET-LUX-APJ-030', 'Aeterna Oltárvédő Sárkánya', '[HORIZONT] celerity; when this entity would be destroyed and go to graveyard, shuffle it into your deck instead; during your next Awakening phase, you may draw 1 extra card for each broken own seal, maximum 2 cards'), ('AET-LUX-APJ-031', 'Lélekmentés', '[GRAVEYARD, HAND] burst: return target entity from your graveyard to your hand'), ('AET-LUX-APJ-039', 'Kórus Dala', '[GRAVEYARD, DECK] choose up to 3 cards in your graveyard; shuffle them into your deck, then draw 1 card'), ('AET-LUX-APJ-043', 'Újjászületés Fénye', "[DOMINIUM, GRAVEYARD] sacrifice 1 allied entity from your Dominium; then put a different entity from your graveyard with magnitude less than or equal to the sacrificed entity's magnitude exhausted into the sacrificed entity's previous slot; this does not count as summoning")]
  - `spell`: [('AET-AQU-MOR-048', 'Megtört Áramlat', 'activation: when opponent plays a spell with burst; effect: counter that spell'), ('AET-AQU-MOR-049', 'Életmentő Burok', 'activation: when allied entity would be destroyed by combat damage or enemy spell or ritual damage; effect: it survives with exactly 1 HP, then may move to empty allied zenit slot if available'), ('AET-AQU-MOR-054', 'Fagyos Tükröződés', "activation: when opponent plays a spell or ritual that would deal damage to you or an allied entity; effect: prevent that damage, then you may draw cards equal to that spell or ritual's magnitude"), ('AET-AQU-ART-002', 'Cseppfolyós Orgyilkos', '[ZENIT] cannot be targeted by enemy spell or ritual; if this moved from Zenit to Horizont this turn, its attacks ignore aegis until end of turn'), ('AET-AQU-ART-007', 'Illúzió-Szirén', '[ZENIT] cannot be targeted by enemy spell or ritual; once during your manifestation phase, target enemy Horizont entity with an enemy Zenit entity behind it in the same lane swaps with that entity'), ('AET-UMB-ARS-038', 'Árnyékba Olvadás', '[DOMINIUM] burst: play when an own Horizont entity becomes the target of an attack or enemy spell/ritual; move that entity to an empty own Zenit slot; if you do, that attack or effect is cancelled'), ('AET-UMB-ARS-045', 'Zsarolás', "[DOMINIUM] look at the opponent's hand; choose 1 spell or ritual card from it; the opponent puts that card into the Void"), ('AET-UMB-ARS-049', 'Váratlan Adóellenőrzés', "activation: when the opponent plays an entity, spell, or ritual from hand; effect: the opponent may exhaust 1 active own source card; if they do not, that played card's effect is cancelled and the card returns to their hand"), ('AET-UMB-ARS-051', 'A Hallgatás Ára', "activation: when the opponent would activate a burst spell from a broken seal; effect: counter that spell's effect, then the opponent exhausts 1 active own source card"), ('AET-VEN-VIH-002', 'Ciklonlovas Cserkész', '[HORIZONT] celerity; [DOMINIUM] when this becomes ready from exhausted by a spell, ritual, or ability, draw 1'), ('AET-VEN-VIH-003', 'Villámlépésű Kardforgató', '[HORIZONT] when this is readied from exhausted by a spell or ritual, it gains +1 ATK until end of turn'), ('AET-VEN-VIH-016', 'Viharfutó Újonc', '[DOMINIUM] clarion: this gains +1 ATK until end of turn if you already played a VENTUS spell this turn'), ('AET-VEN-VIH-041', 'Szelek Tánca', 'draw 1 for each allied entity that became ready from exhausted this turn due to a spell, ritual, or ability'), ('AET-VEN-VIH-052', 'Viharos Visszavágó', 'activation: when the opponent exhausts one or more allied entities with a spell or ritual; effect: that spell or ritual resolves, then all enemy Horizont entities take 2 damage'), ('AET-VEN-VIH-057', 'A Szélvihar Szeme', "while this plane is active, whenever a player's entity becomes ready from exhausted due to a spell, ritual, or ability, that entity gains +1 ATK and +1 max HP until end of turn"), ('AET-VEN-EGU-020', 'Köd-Alak', '[HORIZONT] when this becomes the target of an enemy spell, return it to your hand and counter that spell'), ('AET-VEN-EGU-050', 'Viharos Visszhang', "activation: when your spell or ritual returns an enemy entity to its owner's hand; effect: that opponent discards 1 other card from hand to graveyard"), ('AET-VEN-EGU-051', 'Szétszéledő Köd', 'activation: when an enemy spell or ritual targets your allied ethereal entity; effect: return that entity to your hand and counter that spell or ritual'), ('AET-VEN-EGU-053', 'Váratlan Felszállás', 'activation: when an enemy spell or ritual targets your allied entity in the dominium; effect: return that entity to your hand, then you may draw 1'), ('AET-AET-KOB-027', 'Bérelhető Mágus', '[DOMINIUM] clarion: search your deck for the highest magnitude spell or ritual, put it into your hand, then shuffle your deck')]
  - `spells`: [('AET-AQU-MOR-011', 'Abisszális Ős-Teknős', '[HORIZONT] aegis; [ZENIT] cannot be targeted by enemy spells or rituals'), ('AET-AQU-MOR-030', 'Az Ősforrás Lelke', '[ZENIT] cannot be targeted by enemy spells or rituals; opponent cannot cast burst spells during your turn while this is in zenit'), ('AET-UMB-ARS-002', 'Árnyba Burkolt Kém', '[ZENIT] while this entity is in Zenit, it cannot be targeted by enemy spells or rituals; whenever one of your own seals triggers, this entity gains +1 ATK until end of turn'), ('AET-UMB-ARS-004', 'Éjszemű Varjú', '[ZENIT] harmonize 1; while this entity is in Zenit, it cannot be targeted by enemy spells or rituals'), ('AET-UMB-ARS-007', 'Néma Bérgyilkos', '[ZENIT] while this entity is in Zenit, it cannot be targeted by enemy spells or rituals; [DOMINIUM] if this entity moves from Zenit to Horizont when attacking, it cannot be targeted by enemy spells until end of combat'), ('AET-UMB-ARS-015', 'Noctis az Árnyak Ura', '[HORIZONT] bane; [ZENIT] while this entity is in Zenit, it cannot be targeted by enemy spells or rituals; [DOMINIUM] clarion: search up to 2 UMBRA seals with magnitude 3 or less from your deck or Void, reveal them, then place them face down into empty own Zenit slots; they cannot be activated this turn'), ('AET-UMB-ARS-022', 'Bérgyilkos Mester', '[ZENIT] while this entity is in Zenit, it cannot be targeted by enemy spells or rituals'), ('AET-UMB-ARS-041', 'Az Árnyak Leple', '[DOMINIUM] until end of turn, your entities cannot be targeted by enemy spells or rituals'), ('AET-VEN-VIH-020', 'Széllökések Mestere', '[ZENIT] resonance 2; while this is in Zenit, your VENTUS spells cost 1 less, minimum 0'), ('AET-VEN-VIH-026', 'Vihar-Pajzsos Őrző', '[HORIZONT] aegis; this cannot be exhausted by enemy spells or rituals'), ('AET-VEN-VIH-056', 'Szelek Szentélye', "while this plane is active, each player's spells and rituals that ready an entity cost 1 less, minimum 1"), ('AET-VEN-EGU-019', 'Délibáb Szövő', '[DOMINIUM] clarion: choose up to 1 allied ethereal entity; it cannot be targeted by enemy spells or rituals until end of turn'), ('AET-VEN-EGU-057', 'Felhők Városa', 'while active, enemy spells and rituals cost 1 more aura if they target your allied ethereal entity'), ('AET-AET-FGS-003', 'Lopakodó Felcser-Drón', '[ZENIT] cannot be targeted by enemy spells or rituals; activated ability once during your manifestation phase: target damaged entity in the same lane gains +1 max HP'), ('AET-AET-KOB-004', 'Árnyékos Sikátor Csempésze', '[ZENIT] cannot be targeted by enemy rituals or spells'), ('AET-AET-KOB-026', 'Homokféreg', '[HORIZONT] sundering; cannot be targeted by enemy spells or rituals while on Horizont')]
  - `board`: [('AET-AET-FGS-058', 'A Nagy Óramű Műhely', 'while active, during each of your awakening phases target damaged allied entity on your board heals 2')]

### 19. [P3] CARD_PRINTINGS – CARD_PRINTINGS nem teljes print registry (ha annak szánt)

3 sor vs 814 CARDS_MASTER kártya

### 20. [P3] EXPORT_NOTES – EXPORT_NOTES dátuma régi az 1.8v exporthoz képest

- `Dátum`: 2026-05-20T00:00:00
- `Export verzió`: nincs export
- `Forrás munkalap`: CARDS_MASTER
- `Célfájl`: cards.xlsx
- `Tartalom`: Kapcsolódó munkalapok előkészítése
- `Megjegyzés`: Ez a módosítás még nem runtime-export. A cards.xlsx nem módosul automatikusan.

### 21. [P3] EXPORT_NOTES – Export verzió továbbra is "nincs export"

- `Dátum`: 2026-05-20T00:00:00
- `Export verzió`: nincs export
- `Forrás munkalap`: CARDS_MASTER
- `Célfájl`: cards.xlsx
- `Tartalom`: Kapcsolódó munkalapok előkészítése
- `Megjegyzés`: Ez a módosítás még nem runtime-export. A cards.xlsx nem módosul automatikusan.

### 22. [P3] PRODUCTS/DECKLISTS – Product_ID nincs decklistben (lehet szándékos)

Összesen: 2 tétel.

- KLP-IGN-HAM01
- KZK-CORE01

## Nem hibának minősített, de ellenőrzött pontok

- JSON parse-hiba: nem találtam.
- CARDS_MASTER Szabályi_Kártya_ID duplikáció: nem találtam.
- Print_ID duplikáció: nem találtam.
- Collector_Number duplikáció: nem találtam.
- Nem-Entitás Faj/Kaszt kitöltési hiba: nem találtam.
- Entitás Faj/Kaszt hiány: nem találtam.
- Numerikus mezőhiba: nem találtam.
- Set_ID hivatkozási hiba: nem találtam.
- AETHER záró tartalmak: jelen vannak a JSONL exportban.
