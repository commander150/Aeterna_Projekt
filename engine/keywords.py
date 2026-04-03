from utils.logger import naplo

class KeywordEngine:

    @staticmethod
    def on_summon(egyseg):
        """Amikor egység pályára kerül"""

        if egyseg.lap.van_kulcsszo("Celerity") or egyseg.lap.van_kulcsszo("Gyorsaság"):
            egyseg.kimerult = False
            naplo.ir(f"⚡ {egyseg.lap.nev} azonnal támadhat (Celerity)")

    @staticmethod
    def modify_attack(attacker):
        """Támadás módosítása"""
        bonus = 0

        if attacker.lap.van_kulcsszo("Frenzy"):
            bonus += 1
            naplo.ir(f"🔥 Frenzy +1 ATK")

        return bonus

    @staticmethod
    def on_damage_dealt(attacker, defender):
        """Sebzés után"""

        # 🔪 Sundering (Hasítás)
        if attacker.lap.van_kulcsszo("Hasítás"):
            naplo.ir("💥 Hasítás aktiválódik")

        # ☠️ Bane (Métely)
        if attacker.lap.van_kulcsszo("Métely"):
            defender.bane_target = True
            naplo.ir("☠️ Métely megjelölte a célpontot")

    @staticmethod
    def get_blockers(vedo):
        """Blokkolók kiválasztása (Aegis)"""

        aegis = [
            e for e in vedo.horizont
            if e and not e.kimerult and e.lap.van_kulcsszo("Oltalom")
        ]

        if aegis:
            naplo.ir("🛡️ Aegis kötelező blokkolás")
            return aegis

        return [e for e in vedo.horizont if e and not e.kimerult]