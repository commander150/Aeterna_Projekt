import re
import random
from utils.logger import naplo
from stats.analyzer import stats

class EffectEngine:

    @staticmethod
    def trigger_on_play(kartya, jatekos, ellenfel):
        """Amikor kijátszanak egy lapot (Entitás, Ige, Rituálé), elolvassuk a szövegét."""
        szoveg = kartya.kepesseg.lower()
        if not szoveg or szoveg == "-":
            return

        # 1. LAPHÚZÁS ÉRTELMEZÉSE (pl. "húzz 1 lapot", "húzhatsz 2 lapot")
        # Reguláris kifejezés: keresi a 'húz', majd egy szám, majd a 'lap' szavakat
        huzas_match = re.search(r'(?:húzz|húzhatsz|húz)\s+(\d+)\s+lap', szoveg)
        if huzas_match:
            db = int(huzas_match.group(1))
            naplo.ir(f"✨ Képesség (Laphúzás): {kartya.nev} -> {db} lap")
            for _ in range(db):
                jatekos.huzas()

        # 2. SEBZÉS ÉRTELMEZÉSE (pl. "2 sebzést okoz", "3 sebzés")
        sebzes_match = re.search(r'(\d+)\s+(?:közvetlen\s+)?sebzés', szoveg)
        
        # Csak akkor okozzunk azonnali sebzést, ha ez egy varázslat (Ige/Rituálé) 
        # vagy egy Entitás azonnali Riadó (Clarion) képessége.
        if sebzes_match and (kartya.kartyatipus in ["Ige", "Rituálé"] or "riadó" in szoveg):
            sebzes_ertek = int(sebzes_match.group(1))
            
            # OKOS AI: Keressük meg a legveszélyesebb (legnagyobb ATK-jú) célpontot!
            celpontok = [e for e in ellenfel.horizont if e]
            if celpontok:
                cel = max(celpontok, key=lambda x: x.akt_tamadas)
                naplo.ir(f"🔥 Képesség (Sebzés): {kartya.nev} -> {sebzes_ertek} sebzés {cel.lap.nev}-ba/be")
                
                if cel.serul(sebzes_ertek):
                    naplo.ir(f"☠️ {cel.lap.nev} elpusztult a varázslattól!")
                    ellenfel.horizont[ellenfel.horizont.index(cel)] = None
            else:
                naplo.ir(f"🔥 Képesség (Sebzés): {kartya.nev} -> Nem volt érvényes célpont a Horizonton.")

        # 3. STATISZTIKA NÖVELÉS (pl. "kap +1 ATK-t", "+2 maximális HP-t")
        atk_match = re.search(r'\+(\d+)\s+atk', szoveg)
        if atk_match and "riadó" in szoveg and kartya.egyseg_e:
            bonusz = int(atk_match.group(1))
            # Megkeressük a pályán lévő saját egységet, és megadjuk neki a bónuszt
            for e in jatekos.horizont:
                if e and e.lap.nev == kartya.nev:
                    e.akt_tamadas += bonusz
                    naplo.ir(f"💪 Képesség (Buff): {kartya.nev} kapott +{bonusz} ATK-t!")
                    break
        return None

    @staticmethod
    def trigger_on_trap(jel, tamado_egyseg, tamado, vedo):
        """Amikor egy Jel (Csapda) aktiválódik"""
        szoveg = jel.kepesseg.lower()
        
        # Szöveg értelmezése sebzésre (pl. a csapda X sebzést okoz a támadónak)
        sebzes_match = re.search(r'(\d+)\s+(?:közvetlen\s+)?sebzés', szoveg)
        if sebzes_match:
            sebzes = int(sebzes_match.group(1))
            naplo.ir(f"💥 Csapda: {jel.nev} -> {sebzes} sebzést okoz a támadónak!")
            return tamado_egyseg.serul(sebzes)
        
        # Ha nincs benne szám, akkor valami egyedi hatás. Tesztelés miatt adunk egy defaultot:
        naplo.ir(f"⚠️ Egyedi Csapda: {jel.nev} (Aktiválódott, de nincs számszerűsített sebzése)")
        return False

    @staticmethod
    def trigger_on_burst(kartya, jatekos):
        """Burst (Reakció) aktiválás a Pecsét feltörésekor"""
        szoveg = kartya.kepesseg.lower()
        
        # Burst húzás
        if "húz" in szoveg:
            naplo.ir(f"✨ Burst: {kartya.nev} -> lap húzás")
            jatekos.huzas()

        elif "sebzés" in szoveg:
            naplo.ir(f"🔥 Burst: {kartya.nev} sebzést okoz (nincs célpont logika még)")

        else:
            naplo.ir(f"✨ Burst: {kartya.nev} aktiválódott")