# Aeterna projekt – teljeskörű elemzés és fejlesztési terv

## 1) Rövid állapotkép

A jelenlegi projekt egy **szimuláció-orientált** kártyajáték motor, ahol két AI-játékos (véletlenszerű döntésekkel) játszik egymás ellen. A belépési pont `main.py`, amely Excelből (`cards.xlsx`) tölti a kártyákat, majd több meccset futtat. Emberi játékos-interfész jelenleg nincs, minden döntés random/heurisztikus. A kód már moduláris (loader / engine / simulation / stats), ami jó alap célzott refaktorhoz.

## 2) Jelenlegi architektúra áttekintése

- **Belépési pont**: `main.py` – logfájl indítás, inputfájl ellenőrzés, szimuláció futtatás.
- **Adatbetöltés**: `data/loader.py` – `openpyxl`-lel olvassa a munkafüzet(eke)t, kártyaobjektumokat hoz létre.
- **Játékmag**:
  - `engine/card.py` – kártya és csataegység adatszerkezet.
  - `engine/player.py` – játékosállapot (kéz, pakli, pecsétek, erőforrás, zónák).
  - `engine/game.py` – körvezérlés, kijátszás, harc, pecséttörés, győzelmi logika.
  - `engine/effects.py` és `engine/keyword_rules.py` – képesség- és kulcsszó-feldolgozás.
- **Szimuláció**: `simulation/runner.py` – meccsek tömeges futtatása.
- **Statisztika és napló**: `stats/analyzer.py`, `utils/logger.py`.

## 3) Erősségek

1. **Jó moduláris bontás**: a loader / engine / stats külön van, így tesztelhetőbb részekre bontható.
2. **Szabályok részben elkülönítve**: kulcsszavak külön `KeywordEngine`-ben vannak.
3. **Reprodukálható logolás**: timestampelt naplófájl segíti a hibakeresést.
4. **Domain-specifikus mechanikák megvannak**: pecsétek, zónák, burst, trap, provokáció stb.

## 4) Fő kockázatok és problémák

### 4.1 Tesztelhetőség gyenge (jelenleg)
- Nincs automatizált tesztcsomag (`pytest`/`unittest`).
- Erős a random függés (`random.choice`, `random.random`, kevert pakli), ami nehezíti a determinisztikus tesztet.
- A logolás és `print` oldaleffektjei vegyülnek az üzleti logikával.

### 4.2 Futtatási környezet törékeny
- Függőség (`openpyxl`) nincs deklaráltan menedzselve (pl. `requirements.txt` / `pyproject.toml` hiány).
- Emiatt a program tiszta környezetben azonnal elszállhat import hibával.

### 4.3 Doménlogika túlterhelt helyeken
- `engine/game.py` és `engine/effects.py` mérete/felelőssége nagy; nehéz izoláltan verifikálni.
- A hatások szöveg-parse alapúak, regex és kulcsszó-illesztés dominál: rugalmas, de sérülékeny.

### 4.4 UI/API hiány emberi játékoshoz
- Nincs játékállapot-sorosítás (state snapshot), nincs akciómodell (`PlayCard`, `Attack`, `Pass` mint explicit command).
- A jelenlegi döntések AI-randomra vannak kötve (`kijatszas_fazis`), ez emberi inputnál leválasztandó.

## 5) Elsődleges cél: tesztprogram (javasolt terv)

Az alábbi terv **kódátírás nélkül** készült; implementáció csak külön parancsra ajánlott.

### 5.1 Céltesztek prioritási sorrendben

1. **Smoke / import tesztek**
   - minden modul importálható
   - minimális szimulációs objektum létrehozható

2. **Egységtesztek (pure logic)**
   - `Kartya` szám-konverzió (`magnitudo`, `aura_koltseg`, stb.)
   - `Jatekos.fizet` különböző erőforrás-kombinációkkal
   - `KeywordEngine` kulcsszódetektálás (`Aegis`, `Bane`, `Sundering`)

3. **Szabálytesztek (scenario-based)**
   - pecséttörés + burst aktiváció
   - trap limit és jel-limit
   - provoke/kényszerítés következő körös viselkedése

4. **Determinista integrációs teszt**
   - fix random seed + minimál deck-factory
   - 1-2 kör futtatás és állapotassert

### 5.2 Tesztelési technikák

- **Random kontroll**: seed vagy monkeypatch (`random.choice`, `random.random`).
- **Fixture-gyár**: kézi kártyalétrehozó helper (Excel nélkül).
- **Napló stub**: logger cseréje memóriás gyűjtőre, hogy assertálható legyen esemény.
- **State assertion**: kéz/pakli/temető/horizont/zenit változások ellenőrzése.

### 5.3 Javasolt mappaszerkezet

```text
tests/
  test_card_model.py
  test_player_resource_payment.py
  test_keywords.py
  test_effects_scenarios.py
  test_game_turns.py
  conftest.py
```

## 6) Másodlagos cél: emberi játékos támogatása (terv)

### 6.1 Minimális célarchitektúra

1. **Game State API**
   - Egységes lekérdezhető állapot (mindkét játékos, zónák, kéz, erőforrás, kör).
2. **Action API**
   - Deklaratív akciók: `PLAY_CARD`, `ATTACK`, `SET_TRAP`, `END_PHASE`.
3. **Decision Layer szétválasztás**
   - AI döntő külön osztályban (`RandomBotDecisionPolicy`).
   - Emberi input külön adapterben (`CliDecisionPolicy`).
4. **Validációs réteg**
   - Minden akció előtt szabályellenőrzés (költség, célpont, zónahely, fázis).

### 6.2 Rövid távú megoldás

- **CLI-alapú emberi játék** első iterációban.
- Menüvezérelt kör (`1: lap kijátszás`, `2: támadás`, `3: kör vége`).
- Később erre lehet webes vagy asztali UI-t építeni.

### 6.3 Miért ez a sorrend?

- Tesztek nélkül az emberi input bevezetése gyorsan regresszióhoz vezet.
- Először az akciómodell és validáció legyen kész, utána UI.

## 7) Refaktor stratégia (csak jóváhagyás után)

1. `engine/game.py` bontása fázis-szolgáltatásokra (`draw_phase`, `main_phase`, `combat_phase`).
2. `engine/effects.py` részekre bontása (`damage_effects`, `draw_effects`, `buff_effects`).
3. Döntéshozó stratégiaminta (`IDecisionPolicy`).
4. Excel-függőség kivezetése a maglogikából (tesztekben in-memory deck).

## 8) Mért minőségcélok

- **Teszt lefedettség**: első körben min. 50% kritikus engine-re.
- **Determinista integrációs teszt**: legalább 3 kulcs scenario stabilan menjen.
- **Hibaarány**: fix seed mellett ismételt futások azonos eredményt adjanak.

## 9) Konkrét következő lépések

1. Függőségkezelés rendezése (`requirements.txt` vagy `pyproject.toml`).
2. `tests/` infrastruktúra felvétele és első 5-8 teszteset.
3. Random determinisztikussá tétele tesztmódban.
4. Action API és döntési réteg szétválasztása.
5. CLI emberi játékos MVP.

---

Ha kéred, a következő körben **parancsra** elkészítem:
- (A) minimális, futtatható `pytest` tesztcsomag első verzióját, vagy
- (B) emberi játékos CLI-MVP vázat az AI mellé,

úgy, hogy a jelenlegi szabálymotorral kompatibilis maradjon.
