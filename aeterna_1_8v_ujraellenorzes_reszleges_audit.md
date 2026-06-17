# AETERNA 1.8v javított JSONL export – újraellenőrzési jelentés

## Feldolgozott lapok

- 1. VERZIÓ: 32 sor
- 10. IMPORT_ORIGINAL: 814 sor
- 11. SETS: 3 sor
- 12. PRODUCTS: 22 sor
- 13. CARD_PRINTINGS: 3 sor
- 14. GENERATION_PROFILES: 5 sor
- 15. PRODUCT_DECKLISTS: 754 sor
- 17. NAME_PROFILE: 814 sor
- 3. CARDS_MASTER: 814 sor
- 4. AUDIT_LOG: 185 sor
- 5. LOOKUPS: 29 sor
- 6. RARITY_CODES: 6 sor
- 8. EXPORT_NOTES: 1 sor
- 9. DECISION_LOG: 133 sor

## Alap számlálók

- CARDS_MASTER: 814 sor
- NAME_PROFILE: 814 sor
- PRODUCT_DECKLISTS: 754 sor
- AUDIT_LOG: 185 sor
- DECISION_LOG: 133 sor

### Birodalmi bontás

- AETHER: 116
- AQUA: 118
- IGNIS: 116
- LUX: 116
- TERRA: 116
- UMBRA: 116
- VENTUS: 116

### Klánbontás

- AETHER / Fogaskerék Szövetség: 58
- AETHER / Kóborlók: 58
- AQUA / Mélység Őrzői: 58
- AQUA / Áramlat-táncosok: 60
- IGNIS / Hamvaskezű: 58
- IGNIS / Lángidéző: 58
- LUX / Aeterna Papjai: 58
- LUX / Fényhozó Lovagrend: 58
- TERRA / Vadon Vadászai: 58
- TERRA / Ős-Druidák: 58
- UMBRA / Lélekaratók: 58
- UMBRA / Árnyékszindikátus: 58
- VENTUS / Viharhozók: 58
- VENTUS / Égbolt Úrai: 58

## Korábbi javítások ellenőrzése – kiemelt sorok

- ('AET-AET-KOB-030', 'A Sivatag Ura', '[HORIZONT] sundering; [DOMINIUM] clarion: destroy all face-down enemy Sign cards in Zenit, then you may draw 1 for each destroyed Sign card', 'enemy_face_down_jel', 'destroy, draw', 'sundering, clarion', 'SR', 'CORE01-AET-KOB-030-SR-NF-A1-V1')
- ('AET-AET-KOB-016', 'Utazó Bárd', '[ZENIT] harmonize 1; the supported entity is unaffected by enemy Sign cards', 'own_horizont_entity', 'trap_immunity', 'harmonize', 'U', 'CORE01-AET-KOB-016-U-NF-A1-V1')
- ('AET-AET-KOB-053', 'Váratlan Erősítés', 'when enemy makes a direct attack against one of your seals: prevent the damage, then summon a 1/1 Gepezet token to an empty Horizont slot', 'enemy_entity', 'damage_prevention, summon_token', 'blank', 'U', 'CORE01-AET-KOB-053-U-NF-A1-V1')
- ('AET-AET-FGS-005', 'Karbantartó Pók-Drón', '[ZENIT] harmonize 1', 'self', 'blank', 'harmonize', 'C', 'CORE01-AET-FGS-005-C-NF-A1-V1')
- ('AET-AET-FGS-054', 'Önmegsemmisítő Protokoll', "when your Horizont entity is destroyed by an enemy attack: deal damage to the attacker equal to the destroyed entity's original ATK, minimum 2 maximum 4", 'enemy_entity', 'damage', 'blank', 'U', 'CORE01-AET-FGS-054-U-NF-A1-V1')

## Issue lista

### 1. [P1] CARDS_MASTER – AETHER/egyéb U ritkaságkód maradt

Darab: 58

Státusz: open

Részletek / minták:

- ('AET-AET-FGS-003', 'Lopakodó Felcser-Drón', 'U', 'CORE01-AET-FGS-003-U-NF-A1-V1')
- ('AET-AET-FGS-004', 'Bronzfal Gólem', 'U', 'CORE01-AET-FGS-004-U-NF-A1-V1')
- ('AET-AET-FGS-006', 'Aether-Generátor', 'U', 'CORE01-AET-FGS-006-U-NF-A1-V1')
- ('AET-AET-FGS-009', 'Páncélozott Juggernaut', 'U', 'CORE01-AET-FGS-009-U-NF-A1-V1')
- ('AET-AET-FGS-011', 'Újrahasznosító Egység', 'U', 'CORE01-AET-FGS-011-U-NF-A1-V1')
- ('AET-AET-FGS-016', 'Fémkereső Robotkutya', 'U', 'CORE01-AET-FGS-016-U-NF-A1-V1')
- ('AET-AET-FGS-017', 'Olajozó Drón', 'U', 'CORE01-AET-FGS-017-U-NF-A1-V1')
- ('AET-AET-FGS-020', 'Páncélkovács Mester', 'U', 'CORE01-AET-FGS-020-U-NF-A1-V1')
- ('AET-AET-FGS-021', 'Gyár-Felügyelő', 'U', 'CORE01-AET-FGS-021-U-NF-A1-V1')
- ('AET-AET-FGS-022', 'Rakétás Drón', 'U', 'CORE01-AET-FGS-022-U-NF-A1-V1')
- ('AET-AET-FGS-023', 'Mechanikus Skorpió', 'U', 'CORE01-AET-FGS-023-U-NF-A1-V1')
- ('AET-AET-FGS-024', 'Réz Gólem', 'U', 'CORE01-AET-FGS-024-U-NF-A1-V1')
- ('AET-AET-FGS-032', 'Túlvezérelt Védőmező', 'U', 'CORE01-AET-FGS-032-U-NF-A1-V1')
- ('AET-AET-FGS-033', 'Célzó Szoftver', 'U', 'CORE01-AET-FGS-033-U-NF-A1-V1')
- ('AET-AET-FGS-034', 'Fémolvasztó Sugár', 'U', 'CORE01-AET-FGS-034-U-NF-A1-V1')
- ('AET-AET-FGS-036', 'Vészhelyzeti Gyorsítás', 'U', 'CORE01-AET-FGS-036-U-NF-A1-V1')
- ('AET-AET-FGS-037', 'Rendszer-Kalibrálás', 'U', 'CORE01-AET-FGS-037-U-NF-A1-V1')
- ('AET-AET-FGS-039', 'Fogaskerék-Olajozás', 'U', 'CORE01-AET-FGS-039-U-NF-A1-V1')
- ('AET-AET-FGS-040', 'Túlterhelés', 'U', 'CORE01-AET-FGS-040-U-NF-A1-V1')
- ('AET-AET-FGS-042', 'Szegecsvihar', 'U', 'CORE01-AET-FGS-042-U-NF-A1-V1')
- ('AET-AET-FGS-043', 'Gépiesítés', 'U', 'CORE01-AET-FGS-043-U-NF-A1-V1')
- ('AET-AET-FGS-044', 'Alkatrész-Gyűjtés', 'U', 'CORE01-AET-FGS-044-U-NF-A1-V1')
- ('AET-AET-FGS-047', 'Védelmi Mátrix', 'U', 'CORE01-AET-FGS-047-U-NF-A1-V1')
- ('AET-AET-FGS-048', 'Rövidzárlat', 'U', 'CORE01-AET-FGS-048-U-NF-A1-V1')
- ('AET-AET-FGS-049', 'Túlhevült Kazán', 'U', 'CORE01-AET-FGS-049-U-NF-A1-V1')
- ('AET-AET-FGS-052', 'Rejtett Aknák', 'U', 'CORE01-AET-FGS-052-U-NF-A1-V1')
- ('AET-AET-FGS-053', 'Vészhelyzeti Védőpajzs', 'U', 'CORE01-AET-FGS-053-U-NF-A1-V1')
- ('AET-AET-FGS-054', 'Önmegsemmisítő Protokoll', 'U', 'CORE01-AET-FGS-054-U-NF-A1-V1')
- ('AET-AET-FGS-057', 'A Hulladéktelep', 'U', 'CORE01-AET-FGS-057-U-NF-A1-V1')
- ('AET-AET-FGS-058', 'A Nagy Óramű Műhely', 'U', 'CORE01-AET-FGS-058-U-NF-A1-V1')

### 2. [P1] CARDS_MASTER – Rarity nincs RARITY_CODES listában

Darab: 58

Státusz: open

Részletek / minták:

- ('AET-AET-FGS-003', 'Lopakodó Felcser-Drón', 'U', 'CORE01-AET-FGS-003-U-NF-A1-V1')
- ('AET-AET-FGS-004', 'Bronzfal Gólem', 'U', 'CORE01-AET-FGS-004-U-NF-A1-V1')
- ('AET-AET-FGS-006', 'Aether-Generátor', 'U', 'CORE01-AET-FGS-006-U-NF-A1-V1')
- ('AET-AET-FGS-009', 'Páncélozott Juggernaut', 'U', 'CORE01-AET-FGS-009-U-NF-A1-V1')
- ('AET-AET-FGS-011', 'Újrahasznosító Egység', 'U', 'CORE01-AET-FGS-011-U-NF-A1-V1')
- ('AET-AET-FGS-016', 'Fémkereső Robotkutya', 'U', 'CORE01-AET-FGS-016-U-NF-A1-V1')
- ('AET-AET-FGS-017', 'Olajozó Drón', 'U', 'CORE01-AET-FGS-017-U-NF-A1-V1')
- ('AET-AET-FGS-020', 'Páncélkovács Mester', 'U', 'CORE01-AET-FGS-020-U-NF-A1-V1')
- ('AET-AET-FGS-021', 'Gyár-Felügyelő', 'U', 'CORE01-AET-FGS-021-U-NF-A1-V1')
- ('AET-AET-FGS-022', 'Rakétás Drón', 'U', 'CORE01-AET-FGS-022-U-NF-A1-V1')
- ('AET-AET-FGS-023', 'Mechanikus Skorpió', 'U', 'CORE01-AET-FGS-023-U-NF-A1-V1')
- ('AET-AET-FGS-024', 'Réz Gólem', 'U', 'CORE01-AET-FGS-024-U-NF-A1-V1')
- ('AET-AET-FGS-032', 'Túlvezérelt Védőmező', 'U', 'CORE01-AET-FGS-032-U-NF-A1-V1')
- ('AET-AET-FGS-033', 'Célzó Szoftver', 'U', 'CORE01-AET-FGS-033-U-NF-A1-V1')
- ('AET-AET-FGS-034', 'Fémolvasztó Sugár', 'U', 'CORE01-AET-FGS-034-U-NF-A1-V1')
- ('AET-AET-FGS-036', 'Vészhelyzeti Gyorsítás', 'U', 'CORE01-AET-FGS-036-U-NF-A1-V1')
- ('AET-AET-FGS-037', 'Rendszer-Kalibrálás', 'U', 'CORE01-AET-FGS-037-U-NF-A1-V1')
- ('AET-AET-FGS-039', 'Fogaskerék-Olajozás', 'U', 'CORE01-AET-FGS-039-U-NF-A1-V1')
- ('AET-AET-FGS-040', 'Túlterhelés', 'U', 'CORE01-AET-FGS-040-U-NF-A1-V1')
- ('AET-AET-FGS-042', 'Szegecsvihar', 'U', 'CORE01-AET-FGS-042-U-NF-A1-V1')
- ('AET-AET-FGS-043', 'Gépiesítés', 'U', 'CORE01-AET-FGS-043-U-NF-A1-V1')
- ('AET-AET-FGS-044', 'Alkatrész-Gyűjtés', 'U', 'CORE01-AET-FGS-044-U-NF-A1-V1')
- ('AET-AET-FGS-047', 'Védelmi Mátrix', 'U', 'CORE01-AET-FGS-047-U-NF-A1-V1')
- ('AET-AET-FGS-048', 'Rövidzárlat', 'U', 'CORE01-AET-FGS-048-U-NF-A1-V1')
- ('AET-AET-FGS-049', 'Túlhevült Kazán', 'U', 'CORE01-AET-FGS-049-U-NF-A1-V1')
- ('AET-AET-FGS-052', 'Rejtett Aknák', 'U', 'CORE01-AET-FGS-052-U-NF-A1-V1')
- ('AET-AET-FGS-053', 'Vészhelyzeti Védőpajzs', 'U', 'CORE01-AET-FGS-053-U-NF-A1-V1')
- ('AET-AET-FGS-054', 'Önmegsemmisítő Protokoll', 'U', 'CORE01-AET-FGS-054-U-NF-A1-V1')
- ('AET-AET-FGS-057', 'A Hulladéktelep', 'U', 'CORE01-AET-FGS-057-U-NF-A1-V1')
- ('AET-AET-FGS-058', 'A Nagy Óramű Műhely', 'U', 'CORE01-AET-FGS-058-U-NF-A1-V1')

### 3. [P1] LOOKUPS – CARDS_MASTER Audit_Státusz nincs LOOKUPS-ban

Darab: 8

Státusz: open

Részletek / minták:

- ('adatjavított', 3)
- ('javítva', 53)
- ('szövegjavított_review', 47)
- ('szövegjavított_structured_javított_tesztelendő', 1)
- ('szövegjavított_tesztelendő', 301)
- ('tiszta', 1)
- ('token szabály átvezetve', 2)
- ('átalakított_tesztelendő', 5)

### 4. [P1] LOOKUPS – CARDS_MASTER Klán nincs LOOKUPS-ban

Darab: 2

Státusz: open

Részletek / minták:

- Égbolt Úrai
- Ős-Druidák

### 5. [P1] LOOKUPS – CARDS_MASTER Play_Legal_Status nincs LOOKUPS-ban

Darab: 1

Státusz: open

Részletek / minták:

- ('CORE01_review_required', 123)

### 6. [P1] NAME_PROFILE – NAME_PROFILE mezőeltérés CARDS_MASTER-hez képest

Darab: 24

Státusz: open

Részletek / minták:

- ('AET-IGN-HAM-009', 'Faj', 'Ember vagy Ork', 'Ember')
- ('AET-IGN-HAM-010', 'Faj', 'Ember vagy Ork', 'Ember')
- ('AET-IGN-HAM-010', 'Kaszt', 'Orgyilkos / Harcos', 'Orgyilkos')
- ('AET-IGN-HAM-012', 'Kaszt', 'Harcos vagy Őrző', 'Őrző')
- ('AET-IGN-LAN-004', 'Kaszt', 'Alap', 'Mágus')
- ('AET-IGN-LAN-006', 'Kaszt', 'Alap', 'Kósza')
- ('AET-LUX-FHL-021', 'Kaszt', 'Alap', 'Vadász')
- ('AET-LUX-FHL-024', 'Kaszt', 'Alap', 'Őrző')
- ('AET-LUX-FHL-026', 'Kaszt', 'Alap', 'Harcos')
- ('AET-LUX-FHL-029', 'Kaszt', 'Alap', 'Őrző')
- ('AET-LUX-APJ-003', 'Kaszt', 'Alap', 'Kósza')
- ('AET-LUX-APJ-005', 'Kaszt', 'Alap', 'Őrző')
- ('AET-LUX-APJ-009', 'Kaszt', 'Alap', 'Őrző')
- ('AET-LUX-APJ-023', 'Kaszt', 'Alap', 'Őrző')
- ('AET-LUX-APJ-029', 'Kaszt', 'Alap', 'Őrző')
- ('AET-LUX-APJ-030', 'Kaszt', 'Alap', 'Őrző')
- ('AET-VEN-VIH-011', 'Kaszt', 'Kósza', 'Vadász')
- ('AET-VEN-VIH-023', 'Kaszt', 'Kósza', 'Vadász')
- ('AET-VEN-VIH-027', 'Kaszt', 'Kósza', 'Mágus')
- ('AET-VEN-VIH-030', 'Kaszt', 'Kósza', 'Harcos')
- ('AET-VEN-EGU-008', 'Kaszt', 'Kósza', 'Mágus')
- ('AET-VEN-EGU-011', 'Kaszt', 'Kósza', 'Harcos')
- ('AET-VEN-EGU-021', 'Kaszt', 'Kósza', 'Harcos')
- ('AET-VEN-EGU-029', 'Kaszt', 'Kósza', 'Hős')

### 7. [P1] PRODUCT_DECKLISTS – Nem 40 lapos Deck_ID

Darab: 3

Státusz: open

Részletek / minták:

- ('DECK-AQU-STARTER-001', 41)
- ('DECK-LUX-FHL-TEST-001', 41)
- ('DECK-TER-DRU-TEST-001', 41)

### 8. [P2] CARDS_MASTER – Klán darabszám nem 58

Darab: 1

Státusz: open

Részletek / minták:

- ('AQUA', 'Áramlat-táncosok', 60)

### 9. [P2] CARD_PRINTINGS – CARD_PRINTINGS eltérés CARDS_MASTER-hez képest

Darab: 2

Státusz: open

Részletek / minták:

- ('AET-IGN-HAM-023', 'Play_Legal_Status', 'CORE01_needs_token_rules', 'CORE01_test_required')
- ('AET-IGN-HAM-031', 'Play_Legal_Status', 'CORE01_needs_token_rules', 'CORE01_test_required')

### 10. [P2] DECISION_LOG – Üres Megjegyzés mező

Darab: 3

Státusz: open

Részletek / minták:

- ('D-CORE01-TOKEN-001', 'Token-rendszer alapjátékos státusza')
- ('D-CARDTEXT-SIGN-001', 'Jel lapok természetes szövegformátuma')
- ('D-PLANE-001', 'Sík lapok globális működése')

### 11. [P2] LOOKUPS – Hibakategória token nincs LOOKUPS-ban

Darab: 455

Státusz: open

Részletek / minták:

- ('structured_mezőhiba', 365)
- ('engine_gyanú', 350)
- ('terminológiai_hiba', 283)
- ('szabályszöveg_hiba', 281)
- ('kulcsszó-használati_hiba', 198)
- ('alapadat_hiba', 190)
- ('faj_kaszt_hiba', 41)
- ('Jel_formátum', 20)
- ('státuszkonzisztencia_javítás', 17)
- ('tesztelési_státusz', 17)
- ('laptípusnyelv_hiba', 11)
- ('Üresség_nyelv', 9)
- ('költségcsökkentés', 6)
- ('szabályszöveg_pontosítás', 6)
- ('Reakció_nyelv', 6)
- ('structured_hatáscímke_hiány', 6)
- ('Burst Ige', 5)
- ('EXUL-elhatárolás', 5)
- ('Visszhang_pontosítás', 5)
- ('Kimerült_állapot', 5)
- ('visszaküldés', 5)
- ('Pecsét-sebzés eltávolítva', 4)
- ('időtartam_pontosítás', 4)
- ('Burst_törlés', 4)
- ('structured_trigger_hiány', 4)
- ('attack_nullify', 4)
- ('Sík_globális_pontosítás', 4)
- ('tömeges_visszaküldés', 4)
- ('Sík_hatás', 4)
- ('Hős', 3)

### 12. [P2] NAME_PROFILE – Hiányzó Névforma mező

Darab: 1

Státusz: open

Részletek / minták:

- ('AET-UMB-LEA-037', 'Erőszakos Végzet')

### 13. [P2] PRODUCTS – Teljesen üres / none sor PRODUCTS lapon

Darab: 5

Státusz: open

Részletek / minták:

- 18
- 19
- 20
- 21
- 22

### 14. [P2] PRODUCT_DECKLISTS – Decklist Kártya_Név eltér CARDS_MASTER-től

Darab: 28

Státusz: open

Részletek / minták:

- ('DECK-UMB-ARS-TEST-001', 'AET-UMB-ARS-008', 'Szindikátusi Jelmester', 'Szindikátusi Csapdamester')
- ('DECK-UMB-ARS-TEST-001', 'AET-UMB-ARS-009', 'Árnyközvetítő', 'Árnyék-közvetítő')
- ('DECK-UMB-ARS-TEST-001', 'AET-UMB-ARS-015', 'Noctis, az Árnyak Ura', 'Noctis az Árnyak Ura')
- ('DECK-UMB-ARS-TEST-001', 'AET-UMB-ARS-032', 'Kiszivárgott Titkok', 'Információszivárogtatás')
- ('DECK-UMB-ARS-TEST-001', 'AET-UMB-ARS-037', 'Árnylépés', 'Árnyék-Ugrás')
- ('DECK-UMB-ARS-TEST-001', 'AET-UMB-ARS-039', 'Alvilági Összeköttetések', 'Alvilági Kapcsolatok')
- ('DECK-UMB-ARS-TEST-001', 'AET-UMB-ARS-049', 'Váratlan Sarckivetés', 'Váratlan Adóellenőrzés')
- ('DECK-UMB-LEA-TEST-001', 'AET-UMB-LEA-003', 'Sírnyitó Tanítvány', 'Nekromanta Tanítvány')
- ('DECK-UMB-LEA-TEST-001', 'AET-UMB-LEA-005', 'Morvessa, a Lélekszívó Papnő', 'Lélekszívó Papnő')
- ('DECK-UMB-LEA-TEST-001', 'AET-UMB-LEA-006', 'Feltámadt Csontzúzó', 'Feltámadt Csonttörő')
- ('DECK-UMB-LEA-TEST-001', 'AET-UMB-LEA-015', 'Sírvermi Sírásó', 'Temetői Sírásó')
- ('DECK-UMB-LEA-TEST-001', 'AET-UMB-LEA-024', 'Elyrion, a Lelkek Pásztora', 'Lelkek Pásztora')
- ('DECK-UMB-LEA-TEST-001', 'AET-UMB-LEA-030', 'Azaroth, a Kaszás', 'Azaroth a Kaszás')
- ('DECK-UMB-LEA-TEST-001', 'AET-UMB-LEA-036', 'Ürességből Visszahívás', 'Visszahívás az Ürességből')
- ('DECK-UMB-LEA-TEST-001', 'AET-UMB-LEA-050', 'Sírkőcsapda', 'Sírkő-Csapda')
- ('DECK-UMB-LEA-TEST-001', 'AET-UMB-LEA-056', 'Csontok Szigete', 'Csontvázak Szigete')
- ('DECK-UMB-MIX-TEST-001', 'AET-UMB-ARS-008', 'Szindikátusi Jelmester', 'Szindikátusi Csapdamester')
- ('DECK-UMB-MIX-TEST-001', 'AET-UMB-ARS-015', 'Noctis, az Árnyak Ura', 'Noctis az Árnyak Ura')
- ('DECK-UMB-MIX-TEST-001', 'AET-UMB-LEA-003', 'Sírnyitó Tanítvány', 'Nekromanta Tanítvány')
- ('DECK-UMB-MIX-TEST-001', 'AET-UMB-LEA-005', 'Morvessa, a Lélekszívó Papnő', 'Lélekszívó Papnő')
- ('DECK-UMB-MIX-TEST-001', 'AET-UMB-LEA-024', 'Elyrion, a Lelkek Pásztora', 'Lelkek Pásztora')
- ('DECK-UMB-MIX-TEST-001', 'AET-UMB-ARS-032', 'Kiszivárgott Titkok', 'Információszivárogtatás')
- ('DECK-UMB-MIX-TEST-001', 'AET-UMB-ARS-039', 'Alvilági Összeköttetések', 'Alvilági Kapcsolatok')
- ('DECK-UMB-MIX-TEST-001', 'AET-UMB-ARS-049', 'Váratlan Sarckivetés', 'Váratlan Adóellenőrzés')
- ('DECK-UMB-MIX-TEST-001', 'AET-UMB-LEA-050', 'Sírkőcsapda', 'Sírkő-Csapda')
- ('DECK-UMB-STARTER-001', 'AET-UMB-LEA-006', 'Feltámadt Csontzúzó', 'Feltámadt Csonttörő')
- ('DECK-UMB-STARTER-001', 'AET-UMB-LEA-017', 'Csontpáncélos Harcos', 'Csontváz Harcos')
- ('DECK-UMB-STARTER-001', 'AET-UMB-LEA-018', 'Vérszomjas Denevér', 'Vérszívó Denevér')

### 15. [P3] AUDIT_LOG – Kártya név mező nem pontos CARDS_MASTER kártyanév / összegző tárgyként használt

Darab: 68

Státusz: open

Részletek / minták:

- ('AUD-IGN-HAM-JEL-001', 'Forró Talaj; Robbanó Pajzs; Csapda a Füstben; Hamis Parancs; Tüzes Megtorlás; Lángoló Visszavágás; Csapda a Hamuban; Izzó Aura', 'IGNIS', 'Hamvaskezű')
- ('AUD-IGN-LAN-CLOSE-001', 'Lángidéző klán', 'IGNIS', 'Lángidéző')
- ('AUD-IGN-HAM-CLOSE-001', 'Hamvaskezű klán', 'IGNIS', 'Hamvaskezű')
- ('AUD-IGN-HAM-TOKEN-001', 'Hamvaskezű Toborzó; Goblin Taktika', 'IGNIS', 'Hamvaskezű')
- ('AUD-IGN-DECISION-FIELD-001', 'IGNIS döntésmező-tisztítás', 'IGNIS', 'Hamvaskezű; Lángidéző')
- ('AUD-IGN-STRUCTURED-EXPORT-001', 'IGNIS structured mezők és runtime-export', 'IGNIS', 'Hamvaskezű; Lángidéző')
- ('AUD-IGN-CLOSE-001', 'IGNIS birodalom', 'IGNIS', 'Hamvaskezű; Lángidéző')
- ('AUD-IGN-NAMEPROFILE-001', 'IGNIS névprofil első kör', 'IGNIS', 'Hamvaskezű; Lángidéző')
- ('AUD-AQU-ART-CLOSE-001', 'Áramlat-táncosok klán', 'AQUA', 'Áramlat-táncosok')
- ('AUD-AQU-CLOSE-001', 'AQUA Birodalom', 'AQUA', 'Mélység Őrzői; Áramlat-táncosok')
- ('AUD-TER-DRU-CLOSE-001', 'Ős-Druidák klán', 'TERRA', 'Ős-Druidák')
- ('AUD-TER-WHU-CLOSE-001', 'Vadon Vadászai klán', 'TERRA', 'Vadon Vadászai')
- ('AUD-TER-CLOSE-001', 'TERRA birodalom', 'TERRA', 'Ős-Druidák; Vadon Vadászai')
- ('AUD-LUX-FHL-CLOSE-001', 'Fényhozó Lovagrend klánzárás', 'LUX', 'Fényhozó Lovagrend')
- ('AUD-LUX-APJ-KLANZARAS-20260609', 'Aeterna Papjai klán', 'LUX', 'Aeterna Papjai')
- ('AUD-LUX-BIR-STATUSZTISZTITAS-20260609', 'LUX státusztisztítási csomag', 'LUX', 'Fényhozó Lovagrend; Aeterna Papjai')
- ('AUD-LUX-BIRODALOM-ZARAS-20260609', 'LUX birodalom', 'LUX', 'Fényhozó Lovagrend; Aeterna Papjai')
- ('AUD-LUX-FHL-NAME-001', 'Fényhozó Lovagrend névprofil', 'LUX', 'Fényhozó Lovagrend')
- ('AUD-LUX-APJ-NAME-001', 'Aeterna Papjai névprofil', 'LUX', 'Aeterna Papjai')
- ('AUD-LUX-NAME-RATIO-001', 'LUX néveloszlási arány', 'LUX', 'vegyes')
- ('AUD-LUX-NAME-TERM-001', 'LUX névterminológia', 'LUX', 'vegyes')
- ('AUD-UMB-ARS-001-010', 'Árnyékszindikátus 001–010', 'UMBRA', 'Árnyékszindikátus')
- ('AUD-UMB-ARS-011-020', 'Árnyékszindikátus 011–020', 'UMBRA', 'Árnyékszindikátus')
- ('AUD-UMB-ARS-021-030', 'Árnyékszindikátus 021–030', 'UMBRA', 'Árnyékszindikátus')
- ('AUD-UMB-ARS-031-040', 'Árnyékszindikátus 031–040', 'UMBRA', 'Árnyékszindikátus')
- ('AUD-UMB-ARS-041-050', 'Árnyékszindikátus 041–050', 'UMBRA', 'Árnyékszindikátus')
- ('AUD-UMB-ARS-051-058', 'Árnyékszindikátus 051–058', 'UMBRA', 'Árnyékszindikátus')
- ('AUD-UMB-ARS-IDENTITY', 'Árnyékszindikátus identitásellenőrzés', 'UMBRA', 'Árnyékszindikátus')
- ('AUD-UMB-ARS-TERMINOLOGY', 'Árnyékszindikátus terminológiai tisztítás', 'UMBRA', 'Árnyékszindikátus')
- ('AUD-UMB-ARS-STATUS', 'Árnyékszindikátus play legal státusz', 'UMBRA', 'Árnyékszindikátus')
- ('AUD-UMB-LEA-001-010', 'Lélekaratók 001–010', 'UMBRA', 'Lélekaratók')
- ('AUD-UMB-LEA-011-020', 'Lélekaratók 011–020', 'UMBRA', 'Lélekaratók')
- ('AUD-UMB-LEA-021-030', 'Lélekaratók 021–030', 'UMBRA', 'Lélekaratók')
- ('AUD-UMB-LEA-031-040', 'Lélekaratók 031–040', 'UMBRA', 'Lélekaratók')
- ('AUD-UMB-LEA-041-050', 'Lélekaratók 041–050', 'UMBRA', 'Lélekaratók')
- ('AUD-UMB-LEA-051-058', 'Lélekaratók 051–058', 'UMBRA', 'Lélekaratók')
- ('AUD-UMB-LEA-IDENTITY', 'Lélekaratók identitásellenőrzés', 'UMBRA', 'Lélekaratók')
- ('AUD-UMB-LEA-TERMINOLOGY', 'Lélekaratók terminológiai tisztítás', 'UMBRA', 'Lélekaratók')
- ('AUD-UMB-LEA-STATUS', 'Lélekaratók play legal státusz', 'UMBRA', 'Lélekaratók')
- ('AUD-VEN-VIH-STRUCT-001', 'VENTUS / Viharhozók structured-bővítési jelöltek', 'VENTUS', 'Viharhozók')

### 16. [P3] CARDS_MASTER – Canonical mezőkben régi / nem egységes angol engine-kifejezések

Darab: 77

Státusz: open

Részletek / minták:

- graveyard: 38
- spell: 22
- spells: 16
- board: 1

### 17. [P3] EXPORT_NOTES – EXPORT_NOTES nem tükrözi a JSONL 1.8v exportot

Darab: 1

Státusz: open

Részletek / minták:

- {'Dátum': '2026-05-20T00:00:00', 'Export verzió': 'nincs export', 'Forrás munkalap': 'CARDS_MASTER', 'Célfájl': 'cards.xlsx', 'Tartalom': 'Kapcsolódó munkalapok előkészítése', 'Megjegyzés': 'Ez a módosítás még nem runtime-export. A cards.xlsx nem módosul automatikusan.'}

### 18. [INFO] CARDS_MASTER – burst szerepel Kulcsszavak_Felismerve mezőben (elfogadott döntés szerint kulcsszó/időzítési tulajdonság)

Darab: 42

Státusz: accepted/monitor

Részletek / minták:

- ('AET-IGN-HAM-039', 'Vakító Szikra', 'Ige', 'burst')
- ('AET-IGN-HAM-040', 'Utolsó Szikra', 'Ige', 'burst')
- ('AET-IGN-HAM-043', 'Perzselő Csapás', 'Ige', 'burst')
- ('AET-IGN-HAM-045', 'Lángoló Harag', 'Ige', 'burst')
- ('AET-IGN-LAN-039', 'Láng-Pajzs', 'Ige', 'burst')
- ('AET-IGN-LAN-040', 'Parázs-Szilánk', 'Ige', 'burst')
- ('AET-IGN-LAN-044', 'Lángok Védelme', 'Ige', 'burst')
- ('AET-IGN-LAN-046', 'Váratlan Gyulladás', 'Ige', 'burst')
- ('AET-AQU-MOR-039', 'Védelmező Burok', 'Ige', 'burst')
- ('AET-AQU-MOR-042', 'Hirtelen Dagály', 'Ige', 'aegis, burst')
- ('AET-AQU-MOR-043', 'Megtörhetetlen Hullám', 'Ige', 'burst')
- ('AET-AQU-MOR-046', 'Cunami Visszacsapás', 'Ige', 'burst')
- ('AET-AQU-ART-040', 'Sürgető Hullám', 'Ige', 'burst')
- ('AET-AQU-ART-045', 'Elmosott Nyomok', 'Ige', 'burst')
- ('AET-AQU-ART-047', 'Vissza a Forráshoz', 'Ige', 'burst')
- ('AET-TER-DRU-031', 'Sziklapajzs', 'Ige', 'aegis, burst')
- ('AET-TER-DRU-037', 'Földanyánk Ölelése', 'Ige', 'burst')
- ('AET-TER-WHU-031', 'Gyors Nyílzápor', 'Ige', 'burst')
- ('AET-TER-WHU-036', 'Ösztönös Kitérés', 'Ige', 'burst')
- ('AET-TER-WHU-037', 'Vérszomj', 'Ige', 'aegis, burst')

### 19. [INFO] CARD_PRINTINGS – CARD_PRINTINGS csak részleges / kivétellista-jellegű

Darab: 3

Státusz: known/monitor

Részletek / minták:

- CARDS_MASTER: 814
- CARD_PRINTINGS: 3

### 20. [INFO] PRODUCTS – Product_ID decklist nélkül

Darab: 3

Státusz: intentional/monitor

Részletek / minták:

- BP-CORE01
- KLP-IGN-HAM01
- KZK-CORE01

### 21. [OK] VERZIÓ – 1.8v verziósor megtalálható

Darab: 1

Státusz: closed

Részletek / minták:

- {'Verzió': '1.8v', 'Dátum': '2026-06-15T00:00:00', 'Módosítás típusa': 'AETHER birodalom első teljes kártyaállomány-javító köre, névprofilozása, pakli-előkészítése és kapcsolódó záró logolása lezárva', 'Érintett munkalapok': '3. CARDS_MASTER; 4. AUDIT_LOG; 9. DECISION_LOG; 12. PRODUCTS; 15. PRODUCT_DECKLISTS; 17. NAME_PROFILE; AETHER birodalom; Fogaskerék Szövetség klán; Kóborlók klán', 'Státusz': 'AETHER munkaszinten lezárt, playtestre és későbbi globális balansz-visszaellenőrzésre előkészített állapot', 'Változás leírása': 'A jelen verzióban munkaszinten lezárásra került az AETHER birodalom első teljes kártyaállomány-javító köre. Elkészült a Fogaskerék Szövetség és a Kóborlók klán 58–58 lapos CORE01 állományának CARDS_MASTER-beemelése, a szükséges kártyaszöveg-, structured mező-, státusz-, terminológiai, Kaszt-, Faj-, azonosító- és logikai javításokkal. A Fogaskerék Szövetség identitása Gépezet / Gólem / Kiborg törzsi támogatás, Oltalom, Harmonizálás, Rezonancia, HP-építés, tokenlétrehozás, technikai védelem, board-stabilizálás és kontrollált resource-engine irányban rögzült. A Kóborlók identitása húzás, kézszűrés, tutor, kereskedő / zsoldos / vándor hangulat, reaktív trükkök, resource-rugalmasság, információs előny, Jel-ellenjáték és Pecsétjutalom irányban rögzült. Átvezetésre kerültek az ismert mikrofixek: AET-AET-FGS-005 Harmonizálás 1 egységesítés, AET-AET-FGS-054 Print_Status / Version oszlopjavítás, AET-AET-KOB-030 enemy_face_down_jel structured célpont és Sign card(s) canonical pontosítás, valamint AET-AET-KOB-053 damage_prevention, summon_token hatáscímke. Elkészült az AETHER birodalmi záró AUDIT_LOG és DECISION_LOG, az AETHER NAME_PROFILE első köre mindkét Klánra, a TEST-CORE01-AETHER belső tesztpakli-csoport, a Fogaskerék Szövetség tesztpakli, a Kóborlók tesztpakli, a vegyes AETHER tesztpakli, valamint a BKP-AET01 Product_ID alatt vezetett AETHER kezdőpakli-jelölt.', 'Megjegyzés': 'A verzió nem jelent végleges playtest-, balansz-, runtime-engine-, termék- vagy névátvezetési zárást. Több AETHER lap továbbra is CORE01_review_required vagy CORE01_test_required státuszban maradhat. A NAME_PROFILE lapon szereplő új nevek javaslatok, nem automatikus CARDS_MASTER névátvezetések. A PRODUCT_DECKLISTS paklijai belső tesztelési és kezdőpakli-jelölt státuszú munkalisták, nem végleges kereskedelmi termékek. Az AETHER külön figyelmet igényel a későbbi globális identitásmegőrző balansz-visszaellenőrzésben, mert sok draw, tutor, resource, token, költségcsökkentő és value-engine elemet tartalmaz.'}

