import re
import unicodedata

from engine.card import CsataEgyseg
from utils.logger import naplo


class EffectEngine:

    @staticmethod
    def _normalize_text(szoveg):
        if not szoveg:
            return ""

        normalizalt = unicodedata.normalize("NFKD", str(szoveg))
        normalizalt = "".join(ch for ch in normalizalt if not unicodedata.combining(ch))
        return normalizalt.lower()

    @staticmethod
    def _extract_number(szoveg, mintak):
        for minta in mintak:
            match = re.search(minta, szoveg)
            if match:
                return int(match.group(1))
        return 0

    @staticmethod
    def _collect_units(jatekos):
        egysegek = []

        for index, egyseg in enumerate(jatekos.horizont):
            if isinstance(egyseg, CsataEgyseg):
                egysegek.append(("horizont", index, egyseg))

        for index, egyseg in enumerate(jatekos.zenit):
            if isinstance(egyseg, CsataEgyseg):
                egysegek.append(("zenit", index, egyseg))

        return egysegek

    @staticmethod
    def _destroy_unit(jatekos, zona_nev, index, ok=None):
        zona = jatekos.horizont if zona_nev == "horizont" else jatekos.zenit
        egyseg = zona[index]

        if not isinstance(egyseg, CsataEgyseg):
            return False

        jatekos.temeto.append(egyseg.lap)
        zona[index] = None

        if ok:
            naplo.ir(f"☠️ {egyseg.lap.nev} elpusztult ({ok})")

        return True

    @staticmethod
    def _find_matching_ally(jatekos, kartya=None):
        egysegek = EffectEngine._collect_units(jatekos)
        if not egysegek:
            return None

        if kartya is not None:
            for zona_nev, index, egyseg in egysegek:
                if egyseg.lap.nev == kartya.nev:
                    return zona_nev, index, egyseg

        return max(egysegek, key=lambda adat: (adat[2].akt_tamadas, adat[2].akt_hp))

    @staticmethod
    def _select_enemy_target(ellenfel):
        if ellenfel is None:
            return None

        horizont = [
            ("horizont", index, egyseg)
            for index, egyseg in enumerate(ellenfel.horizont)
            if isinstance(egyseg, CsataEgyseg)
        ]
        if horizont:
            return max(horizont, key=lambda adat: (adat[2].akt_tamadas, adat[2].akt_hp))

        zenit = [
            ("zenit", index, egyseg)
            for index, egyseg in enumerate(ellenfel.zenit)
            if isinstance(egyseg, CsataEgyseg)
        ]
        if zenit:
            return max(zenit, key=lambda adat: (adat[2].akt_tamadas, adat[2].akt_hp))

        return None

    @staticmethod
    def _deal_damage_to_target(forras_nev, sebzes, cel_adat, ellenfel, kontextus):
        if cel_adat is None or ellenfel is None or sebzes <= 0:
            return False

        zona_nev, index, cel = cel_adat
        naplo.ir(f"🔥 {kontextus}: {forras_nev} -> {sebzes} sebzés {cel.lap.nev}-ba/be")

        if cel.serul(sebzes):
            return EffectEngine._destroy_unit(ellenfel, zona_nev, index, kontextus.lower())

        return False

    @staticmethod
    def _resolve_draw(kartya, jatekos, szoveg, kontextus):
        huzas_db = EffectEngine._extract_number(szoveg, [
            r'(?:huzz|huzhatsz|huzol|huz)\s+(\d+)\s+lap',
            r'(\d+)\s+lapot?\s+(?:huzz|huzhatsz|huzol|huz)',
            r'draw\s+(\d+)',
        ])

        if huzas_db <= 0:
            return False

        naplo.ir(f"✨ {kontextus}: {kartya.nev} -> {huzas_db} lap húzás")
        for _ in range(huzas_db):
            jatekos.huzas()
        return True

    @staticmethod
    def _resolve_damage(kartya, jatekos, ellenfel, szoveg, kontextus, engedelyezett):
        if not engedelyezett:
            return False

        sebzes = EffectEngine._extract_number(szoveg, [
            r'(\d+)\s+(?:kozvetlen\s+)?sebzes',
            r'okoz\s+(\d+)\s+sebzest',
            r'sebez\s+(\d+)',
            r'(\d+)\s+damage',
        ])

        if sebzes <= 0:
            return False

        cel = EffectEngine._select_enemy_target(ellenfel)
        if cel is None:
            naplo.ir(f"🔥 {kontextus}: {kartya.nev} -> Nem volt érvényes célpont.")
            return False

        EffectEngine._deal_damage_to_target(kartya.nev, sebzes, cel, ellenfel, kontextus)
        return True

    @staticmethod
    def _resolve_buff(kartya, jatekos, szoveg, kontextus):
        atk_bonusz = EffectEngine._extract_number(szoveg, [
            r'\+(\d+)\s*atk',
            r'kap\s+\+(\d+)\s*atk',
            r'(\d+)\s*atk-t\s+kap',
            r'\+(\d+)\s*tamadas',
        ])
        hp_bonusz = EffectEngine._extract_number(szoveg, [
            r'\+(\d+)\s*(?:hp|eletero)',
            r'kap\s+\+(\d+)\s*(?:hp|eletero)',
            r'(\d+)\s*(?:hp|eletero)-t\s+kap',
        ])

        if atk_bonusz <= 0 and hp_bonusz <= 0:
            return False

        cel = EffectEngine._find_matching_ally(jatekos, kartya)
        if cel is None:
            naplo.ir(f"✨ {kontextus}: {kartya.nev} -> Nincs saját egység a bónuszhoz.")
            return False

        _, _, egyseg = cel

        if atk_bonusz > 0:
            egyseg.akt_tamadas += atk_bonusz
            naplo.ir(f"💪 {kontextus}: {egyseg.lap.nev} +{atk_bonusz} ATK")

        if hp_bonusz > 0:
            egyseg.akt_hp += hp_bonusz
            naplo.ir(f"🛡️ {kontextus}: {egyseg.lap.nev} +{hp_bonusz} HP")

        return True

    @staticmethod
    def _resolve_heal(kartya, jatekos, szoveg, kontextus):
        gyogyitas = EffectEngine._extract_number(szoveg, [
            r'gyogy(?:it|its)?\s+(\d+)',
            r'(\d+)\s*(?:hp|eletero)\s+gyogyul',
            r'heal\s+(\d+)',
        ])

        if gyogyitas <= 0:
            return False

        cel = EffectEngine._find_matching_ally(jatekos, kartya)
        if cel is None:
            naplo.ir(f"✨ {kontextus}: {kartya.nev} -> Nem volt gyógyítható saját egység.")
            return False

        _, _, egyseg = cel
        egyseg.akt_hp += gyogyitas
        naplo.ir(f"💚 {kontextus}: {egyseg.lap.nev} gyógyult {gyogyitas} HP-t")
        return True

    @staticmethod
    def _resolve_resource_gain(kartya, jatekos, szoveg, kontextus):
        if "osforras" not in szoveg and "aura" not in szoveg:
            return False

        if not jatekos.pakli:
            return False

        if "kap" not in szoveg and "letrehoz" not in szoveg and "hozzaad" not in szoveg:
            return False

        lap = jatekos.pakli.pop()
        jatekos.osforras.append({"lap": lap, "hasznalt": False})
        naplo.ir(f"🔋 {kontextus}: {kartya.nev} +1 Ősforrás ({lap.nev})")
        return True

    @staticmethod
    def _resolve_common_effects(kartya, jatekos, ellenfel, szoveg, kontextus, engedelyezett_sebzes):
        tortent_valami = False
        tortent_valami |= EffectEngine._resolve_draw(kartya, jatekos, szoveg, kontextus)
        tortent_valami |= EffectEngine._resolve_damage(
            kartya, jatekos, ellenfel, szoveg, kontextus, engedelyezett_sebzes
        )
        tortent_valami |= EffectEngine._resolve_buff(kartya, jatekos, szoveg, kontextus)
        tortent_valami |= EffectEngine._resolve_heal(kartya, jatekos, szoveg, kontextus)
        tortent_valami |= EffectEngine._resolve_resource_gain(kartya, jatekos, szoveg, kontextus)
        return tortent_valami

    @staticmethod
    def trigger_on_play(kartya, jatekos, ellenfel):
        """Amikor kijátszanak egy lapot, megpróbáljuk értelmezni a szövegét."""
        nyers_szoveg = kartya.kepesseg
        szoveg = EffectEngine._normalize_text(nyers_szoveg)
        if not szoveg or szoveg == "-":
            return None

        sebzes_engedelyezett = (
            kartya.kartyatipus in ["Ige", "Rituálé"]
            or "riado" in szoveg
            or "clarion" in szoveg
        )

        EffectEngine._resolve_common_effects(
            kartya, jatekos, ellenfel, szoveg, "Képesség", sebzes_engedelyezett
        )
        return None

    @staticmethod
    def trigger_on_trap(jel, tamado_egyseg, tamado, vedo):
        """Amikor egy Jel aktiválódik a támadó ellen."""
        szoveg = EffectEngine._normalize_text(jel.kepesseg)
        if not szoveg or szoveg == "-":
            return False

        meghalt = False
        sebzes = EffectEngine._extract_number(szoveg, [
            r'(\d+)\s+(?:kozvetlen\s+)?sebzes',
            r'okoz\s+(\d+)\s+sebzest',
            r'sebez\s+(\d+)',
        ])
        if sebzes > 0:
            naplo.ir(f"💥 Csapda: {jel.nev} -> {sebzes} sebzést okoz a támadónak!")
            meghalt = tamado_egyseg.serul(sebzes)

        atk_csokkentes = EffectEngine._extract_number(szoveg, [
            r'-(\d+)\s*atk',
            r'veszit\s+(\d+)\s*atk',
            r'csokkenti\s+(\d+)\s*atk',
        ])
        if atk_csokkentes > 0:
            tamado_egyseg.akt_tamadas = max(0, tamado_egyseg.akt_tamadas - atk_csokkentes)
            naplo.ir(f"🕸️ Csapda: {jel.nev} -> -{atk_csokkentes} ATK a támadónak")

        if "kimerit" in szoveg or "stun" in szoveg or "fagyaszt" in szoveg:
            tamado_egyseg.kimerult = True
            naplo.ir(f"🧊 Csapda: {jel.nev} -> a támadó kimerült")

        if "megsemmisit" in szoveg or "elpusztit" in szoveg or "pusztitsd el" in szoveg:
            naplo.ir(f"☠️ Csapda: {jel.nev} -> a támadó megsemmisül")
            meghalt = True

        EffectEngine._resolve_draw(jel, vedo, szoveg, "Csapda")
        EffectEngine._resolve_heal(jel, vedo, szoveg, "Csapda")

        if not meghalt and sebzes <= 0 and atk_csokkentes <= 0:
            naplo.ir(f"⚠️ Egyedi Csapda: {jel.nev} aktiválódott, de nem volt ismert konkrét hatása")

        return meghalt

    @staticmethod
    def trigger_on_burst(kartya, jatekos, ellenfel=None):
        """Burst (Reakció) aktiválás a pecsét feltörésekor."""
        szoveg = EffectEngine._normalize_text(kartya.kepesseg)
        if not szoveg or szoveg == "-":
            return False

        tortent_valami = EffectEngine._resolve_common_effects(
            kartya, jatekos, ellenfel, szoveg, "Burst", True
        )

        if not tortent_valami:
            naplo.ir(f"✨ Burst: {kartya.nev} aktiválódott")

        return tortent_valami
