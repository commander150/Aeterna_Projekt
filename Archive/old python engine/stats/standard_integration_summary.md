# Új táblázat-szabvány integráció összefoglaló

## Módosított fájlok

- `data/loader.py`
- `engine/card.py`
- `engine/card_metadata.py`
- `engine/structured_effects.py`
- `tests/test_card_model.py`
- `tests/test_structured_effects.py`

## Mit állított át a rendszer

- A `cards.xlsx` 22 oszlopos szerkezetét név-alapú fejlécekkel kezeli.
- A loader normalizálja a listás mezőket, a számokat és a `blank` / `none` üresjelöléseket.
- A `Kartya` modell explicit módon tartalmazza a canonical, zone, keyword, trigger, target, effect tag, duration, condition, machine description, interpretation status és engine notes mezőket.
- A structured effect réteg már a felismert zónákat és az időtartam egy részét is figyelembe veszi.
- A loader validációs figyelmeztetéseket ad ismeretlen enum értékekre és gyanús kombinációkra.

## Jelenlegi cards.xlsx összkép

- Betöltött sorok száma: `814`
- Validációs figyelmeztetések: `471`

### Kártyatípus megoszlás

- `Entitás`: `420`
- `Rituálé`: `113`
- `Ige`: `113`
- `Jel`: `112`
- `Sík`: `56`

### Értelmezési státusz megoszlás

- `osszetett_egyedi`: `478`
- `elso_koros_gepi_ertelmezes`: `193`
- `passziv_vagy_egyszeru`: `88`
- `folyamatos_sik_hatas`: `55`

### Validációs minta

- `sheet=IGNIS row=2 idotartam_hatascimke_nelkul`
- `sheet=IGNIS row=15 idotartam_hatascimke_nelkul`
- `sheet=IGNIS row=23 idotartam_hatascimke_nelkul`
- `sheet=IGNIS row=24 ismeretlen_ertek:hatascimkek:summon`
- `sheet=IGNIS row=29 ismeretlen_ertek:idotartam_felismerve:until_next_enemy_turn`
- `sheet=IGNIS row=32 ismeretlen_ertek:hatascimkek:summon`
- `sheet=IGNIS row=34 ismeretlen_ertek:idotartam_felismerve:until_next_enemy_turn`
- `sheet=IGNIS row=35 ismeretlen_ertek:hatascimkek:sacrifice`
- `sheet=IGNIS row=39 ismeretlen_ertek:hatascimkek:sacrifice`
- `sheet=IGNIS row=51 ismeretlen_ertek:hatascimkek:redirect`
- `sheet=IGNIS row=55 ismeretlen_ertek:hatascimkek:counterspell`
- `sheet=IGNIS row=56 ismeretlen_ertek:hatascimkek:summon_restrict`
- `sheet=IGNIS row=60 ismeretlen_ertek:hatascimkek:resource_gain`
- `sheet=IGNIS row=65 ismeretlen_ertek:hatascimkek:summon`
- `sheet=IGNIS row=65 ismeretlen_ertek:idotartam_felismerve:next_own_awakening`
- `sheet=IGNIS row=66 idotartam_hatascimke_nelkul`
- `sheet=IGNIS row=67 ismeretlen_ertek:hatascimkek:untargetable`
- `sheet=IGNIS row=68 ismeretlen_ertek:hatascimkek:untargetable`
- `sheet=IGNIS row=69 ismeretlen_ertek:hatascimkek:free_cast`
- `sheet=IGNIS row=69 gyanus_target_tipus_kombinacio:own_hand`
- `sheet=IGNIS row=70 ismeretlen_ertek:hatascimkek:damage_bonus`
- `sheet=IGNIS row=70 gyanus_target_tipus_kombinacio:own_hand`
- `sheet=IGNIS row=71 gyanus_target_tipus_kombinacio:own_hand`
- `sheet=IGNIS row=72 ismeretlen_ertek:hatascimkek:source_manipulation`
- `sheet=IGNIS row=73 ismeretlen_ertek:hatascimkek:source_manipulation`
- `... további 446 figyelmeztetés`