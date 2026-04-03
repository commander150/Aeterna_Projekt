import unicodedata

from utils.logger import naplo


class KeywordEngine:

    @staticmethod
    def _normalize(szoveg):
        if not szoveg:
            return ""

        normalizalt = unicodedata.normalize("NFKD", str(szoveg))
        normalizalt = "".join(ch for ch in normalizalt if not unicodedata.combining(ch))
        return normalizalt.lower()

    @staticmethod
    def _has_keyword(forras, *kulcsszavak):
        kepesseg = KeywordEngine._normalize(
            getattr(forras.lap, "kepesseg", getattr(forras, "kepesseg", ""))
        )
        return any(KeywordEngine._normalize(kulcsszo) in kepesseg for kulcsszo in kulcsszavak)

    @staticmethod
    def on_summon(egyseg):
        """Amikor egység pályára kerül."""
        if KeywordEngine._has_keyword(egyseg, "Celerity", "Gyorsaság"):
            egyseg.kimerult = False
            naplo.ir(f"⚡ {egyseg.lap.nev} azonnal támadhat (Celerity)")

    @staticmethod
    def modify_attack(attacker):
        """Általános támadás módosítók."""
        bonus = 0

        if KeywordEngine._has_keyword(attacker, "Frenzy"):
            bonus += 1
            naplo.ir("🔥 Frenzy +1 ATK")

        return bonus

    @staticmethod
    def get_harmonize_bonus(attacker, support_unit):
        """Harmonizálás / Harmonize bónusz számítása."""
        if support_unit is None:
            return 0

        if not KeywordEngine._has_keyword(support_unit, "Harmonizálás", "Harmonize"):
            return 0

        if support_unit.lap.magnitudo <= 4:
            bonusz = 2
        elif support_unit.lap.magnitudo <= 8:
            bonusz = 1
        else:
            bonusz = 0

        if bonusz > 0:
            naplo.ir(f"🎶 Harmonizálás +{bonusz} ATK")

        return bonusz

    @staticmethod
    def on_damage_dealt(attacker, defender):
        """Sebzés után futó kulcsszó-horgok."""
        if KeywordEngine._has_keyword(attacker, "Hasítás", "Sundering"):
            naplo.ir("💢 Hasítás aktiválódik")

        if KeywordEngine._has_keyword(attacker, "Métely", "Bane"):
            defender.bane_target = True
            naplo.ir("☠️ Métely megjelölte a célpontot")

    @staticmethod
    def get_blockers(vedo):
        """Blokkolók kiválasztása (Aegis / Oltalom)."""
        aegis = [
            e for e in vedo.horizont
            if e and not e.kimerult and KeywordEngine._has_keyword(e, "Oltalom", "Aegis")
        ]

        if aegis:
            naplo.ir("🛡️ Aegis kötelező blokkolás")
            return aegis

        return [e for e in vedo.horizont if e and not e.kimerult]

    @staticmethod
    def filter_blockers_for_attacker(attacker, blockers):
        """Légies / Ethereal alapján szűri a blokkolókat."""
        if not KeywordEngine._has_keyword(attacker, "Légies", "Ethereal"):
            return blockers

        ervenyes = [
            blocker for blocker in blockers
            if KeywordEngine._has_keyword(blocker, "Légies", "Ethereal")
        ]
        naplo.ir("👻 Csak légies blokkolhat")
        return ervenyes

    @staticmethod
    def resolve_bane(attacker, defender, destroy_defender):
        """Métely / Bane utólagos megsemmisítés."""
        if defender is None or not getattr(defender, "bane_target", False):
            return False

        if not KeywordEngine._has_keyword(attacker, "Métely", "Bane"):
            return False

        if destroy_defender():
            naplo.ir(f"☠️ Métely: {defender.lap.nev} a fázis végéig elpusztul")
            return True

        return False

    @staticmethod
    def resolve_sundering(attacker, defender_died_from_damage, break_extra_seal):
        """Hasítás / Sundering extra pecséttörés."""
        if not defender_died_from_damage:
            return False

        if not KeywordEngine._has_keyword(attacker, "Hasítás", "Sundering"):
            return False

        return break_extra_seal()
