import re
import unicodedata

from engine.card import CsataEgyseg
from stats.analyzer import stats
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
    def _contains_any(szoveg, kulcsszavak):
        return any(kulcsszo in szoveg for kulcsszo in kulcsszavak)

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
    def _get_zone(jatekos, zona_nev):
        if zona_nev == "horizont":
            return jatekos.horizont
        if zona_nev == "zenit":
            return jatekos.zenit
        raise ValueError(f"Ismeretlen zona: {zona_nev}")

    @staticmethod
    def destroy_unit(jatekos, zona_nev, index, ellenfel=None, ok=None):
        zona = EffectEngine._get_zone(jatekos, zona_nev)
        egyseg = zona[index]

        if not isinstance(egyseg, CsataEgyseg):
            return False

        jatekos.temeto.append(egyseg.lap)
        zona[index] = None

        if ok:
            naplo.ir(f"☠️ {egyseg.lap.nev} elpusztult ({ok})")

        EffectEngine.trigger_on_death(egyseg.lap, jatekos, ellenfel)
        return True

    @staticmethod
    def _resolve_temporary_aura(kartya, jatekos, szoveg, kontextus):
        aura_szavak = ["ideiglenes aura", "temporary aura", "rezonancia aura", "plusz aura", "extra aura"]
        if not EffectEngine._contains_any(szoveg, aura_szavak):
            return False

        mennyiseg = EffectEngine._extract_number(szoveg, [
            r'(\d+)\s+(?:ideiglenes\s+)?aura',
            r'kap\s+(\d+)\s+aura',
            r'(\d+)\s+temporary\s+aura',
            r'(\d+)\s+rezonancia aura',
        ])
        if mennyiseg <= 0:
            mennyiseg = 1

        return jatekos.ad_ideiglenes_aurat(mennyiseg, f"{kontextus}: {kartya.nev}") > 0

    @staticmethod
    def _resolve_reactivate(kartya, jatekos, szoveg, kontextus):
        reaktivalas_szavak = ["ujraaktival", "reaktival", "untap", "ready", "frissit", "ujra kesz"]
        if not EffectEngine._contains_any(szoveg, reaktivalas_szavak):
            return False

        jeloltek = [
            adat for adat in EffectEngine._collect_units(jatekos)
            if adat[2].kimerult
        ]
        if not jeloltek:
            naplo.ir(f"{kontextus}: {kartya.nev} -> Nem volt újraaktiválható saját egység.")
            return False

        _, _, egyseg = max(jeloltek, key=lambda adat: (adat[2].akt_tamadas, adat[2].akt_hp))
        return jatekos.ujraaktivalt_egyseget(egyseg, f"{kontextus}: {kartya.nev}")

    @staticmethod
    def _resolve_provoke(kartya, jatekos, ellenfel, szoveg, kontextus):
        if ellenfel is None:
            return False

        provoke_szovegek = [
            "kenyszerites",
            "provoke",
            "tamadnia kell",
            "must attack",
            "next turn if able",
            "kovetkezo korben tamad",
        ]
        if not EffectEngine._contains_any(szoveg, provoke_szovegek):
            return False

        ellenfel.kell_tamadnia_kovetkezo_korben = True
        naplo.ir(
            f"{kontextus}: {kartya.nev} Kényszerítés/Provoke hatást alkalmazott {ellenfel.nev} játékosra"
        )
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
    def _enemy_targeting_mode(szoveg):
        if any(k in szoveg for k in ["kimerult", "exhausted", "stunned"]):
            return "exhausted"
        if any(k in szoveg for k in ["leggyengebb", "weakest", "legalacsonyabb hp"]):
            return "weakest"
        return "strongest"

    @staticmethod
    def _pick_enemy_target(jeloltek, mod):
        if not jeloltek:
            return None
        if mod == "weakest":
            return min(jeloltek, key=lambda adat: (adat[2].akt_hp, adat[2].akt_tamadas))
        if mod == "exhausted":
            faradtak = [adat for adat in jeloltek if adat[2].kimerult]
            if faradtak:
                return max(faradtak, key=lambda adat: (adat[2].akt_tamadas, adat[2].akt_hp))
        return max(jeloltek, key=lambda adat: (adat[2].akt_tamadas, adat[2].akt_hp))

    @staticmethod
    def _mark_overflow_defeat(vedo, tamado, kontextus, forras_nev):
        if vedo is None:
            return False

        vedo.overflow_vereseg = True
        vedo.overflow_gyoztes_nev = getattr(tamado, "nev", None)
        naplo.ir(f"☠️ {kontextus}: {forras_nev} Overflow győzelmet okozott")
        return True

    @staticmethod
    def trigger_on_death(kartya, jatekos, ellenfel=None):
        """Halálkor aktiválódó képességek, pl. Echo / Visszhang."""
        szoveg = EffectEngine._normalize_text(getattr(kartya, "kepesseg", ""))
        if not szoveg or szoveg == "-":
            return False

        match = re.search(r'(?:visszhang|echo)\s*[:\-]?\s*(.+)', szoveg)
        if not match:
            return False

        death_text = match.group(1).strip()
        naplo.ir(f"✨ Halál effekt: {kartya.nev} (Echo/Visszhang)")

        if not death_text:
            return True

        tortent_valami = EffectEngine._resolve_common_effects(
            kartya, jatekos, ellenfel, death_text, "Halál effekt", True
        )

        if not tortent_valami:
            naplo.ir(f"✨ Halál effekt: {kartya.nev} aktiválódott")

        return True

    @staticmethod
    def _select_enemy_target(ellenfel, szoveg="", prefer_zone=None):
        if ellenfel is None:
            return None

        horizont = [
            ("horizont", index, egyseg)
            for index, egyseg in enumerate(ellenfel.horizont)
            if isinstance(egyseg, CsataEgyseg)
        ]
        zenit = [
            ("zenit", index, egyseg)
            for index, egyseg in enumerate(ellenfel.zenit)
            if isinstance(egyseg, CsataEgyseg)
        ]

        jeloltek = horizont + zenit
        if prefer_zone == "horizont" and horizont:
            jeloltek = horizont
        elif prefer_zone == "zenit" and zenit:
            jeloltek = zenit

        return EffectEngine._pick_enemy_target(
            jeloltek, EffectEngine._enemy_targeting_mode(szoveg)
        )

    @staticmethod
    def _targets_player_or_seal(szoveg):
        return EffectEngine._contains_any(
            szoveg,
            [
                "pecset",
                "seal",
                "ward",
                "wards",
                "enemy player",
                "opposing player",
                "ellenfel jatekos",
                "jatekost",
                "ellenfel pecsete",
            ],
        )

    @staticmethod
    def _break_seal_from_effect(vedo, tamado, kartya_nev, kontextus, burst_aktivalt):
        if vedo is None or not vedo.pecsetek:
            return False, burst_aktivalt

        p = vedo.pecsetek.pop()
        stats.feltort_pecsetek += 1

        if p.magnitudo > len(vedo.osforras):
            vedo.osforras.append({"lap": p, "hasznalt": False})
            naplo.ir(f"✨ {kontextus}: {kartya_nev} + Gondviselés ({p.nev})")
        else:
            vedo.kez.append(p)
            naplo.ir(f"💔 {kontextus}: {kartya_nev} feltört egy Pecsétet ({p.nev})")

        if p.reakcio_e and not burst_aktivalt:
            naplo.ir("✨ Reakció (Burst) aktiválódik")
            EffectEngine.trigger_on_burst(p, vedo, tamado)
            burst_aktivalt = True

        return True, burst_aktivalt

    @staticmethod
    def _deal_direct_seal_damage(kartya_nev, sebzes, tamado, vedo, kontextus):
        if vedo is None or sebzes <= 0:
            return False

        naplo.ir(f"🔥 {kontextus}: {kartya_nev} közvetlenül {sebzes} sebzést okoz {vedo.nev} Pecsétjeinek")

        if not vedo.pecsetek:
            return EffectEngine._mark_overflow_defeat(vedo, tamado, kontextus, kartya_nev)

        burst_aktivalt = False
        feltort_db = 0
        maradek_sebzes = sebzes

        while maradek_sebzes > 0 and vedo.pecsetek:
            pecset_tort, burst_aktivalt = EffectEngine._break_seal_from_effect(
                vedo, tamado, kartya_nev, kontextus, burst_aktivalt
            )
            if not pecset_tort:
                break

            feltort_db += 1
            maradek_sebzes -= 1

            if vedo.overflow_vereseg or getattr(tamado, "overflow_vereseg", False):
                break

        if feltort_db > 0:
            naplo.ir(f"💥 {kontextus}: {kartya_nev} összesen {feltort_db} Pecsétet tört fel")

        if maradek_sebzes > 0 and not vedo.pecsetek:
            EffectEngine._mark_overflow_defeat(vedo, tamado, kontextus, kartya_nev)

        return feltort_db > 0 or vedo.overflow_vereseg

    @staticmethod
    def _deal_damage_to_target(forras_nev, sebzes, cel_adat, ellenfel, kontextus, forras_jatekos=None):
        if cel_adat is None or ellenfel is None or sebzes <= 0:
            return False

        zona_nev, index, cel = cel_adat
        naplo.ir(f"🔥 {kontextus}: {forras_nev} -> {sebzes} sebzés {cel.lap.nev}-ba/be")

        if cel.serul(sebzes):
            return EffectEngine.destroy_unit(
                ellenfel, zona_nev, index, forras_jatekos, kontextus.lower()
            )

        return False

    @staticmethod
    def _destroy_target(cel_adat, jatekos, ellenfel, kontextus):
        if cel_adat is None or ellenfel is None:
            return False

        zona_nev, index, cel = cel_adat
        naplo.ir(f"{kontextus}: {cel.lap.nev} megsemmisul")
        return EffectEngine.destroy_unit(ellenfel, zona_nev, index, jatekos, kontextus.lower())

    @staticmethod
    def _resolve_destroy(kartya, jatekos, ellenfel, szoveg, kontextus):
        if not any(k in szoveg for k in ["megsemmisit", "elpusztit", "destroy", "pusztitsd el"]):
            return False

        cel = EffectEngine._select_enemy_target(ellenfel, szoveg)
        if cel is None:
            naplo.ir(f"{kontextus}: {kartya.nev} -> Nem volt megsemmisitheto celpont.")
            return False

        return EffectEngine._destroy_target(cel, jatekos, ellenfel, kontextus)

    @staticmethod
    def _resolve_exhaust(kartya, jatekos, ellenfel, szoveg, kontextus):
        if not any(k in szoveg for k in ["kimerit", "stun", "fagyaszt", "exhaust"]):
            return False

        cel = EffectEngine._select_enemy_target(ellenfel, "strongest")
        if cel is None:
            naplo.ir(f"{kontextus}: {kartya.nev} -> Nem volt kimeritheto celpont.")
            return False

        _, _, egyseg = cel
        egyseg.kimerult = True
        naplo.ir(f"{kontextus}: {kartya.nev} kimeritette {egyseg.lap.nev} egyseget")
        return True

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
        tortent = False
        for _ in range(huzas_db):
            tortent |= bool(jatekos.huzas(extra=True))
        return tortent

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

        if EffectEngine._targets_player_or_seal(szoveg):
            return EffectEngine._deal_direct_seal_damage(
                kartya.nev, sebzes, jatekos, ellenfel, kontextus
            )

        prefer_zone = "horizont" if any(k in szoveg for k in ["horizont", "front", "elso sor"]) else None
        cel = EffectEngine._select_enemy_target(ellenfel, szoveg, prefer_zone)
        if cel is None:
            naplo.ir(f"🔥 {kontextus}: {kartya.nev} -> Nem volt érvényes célpont.")
            return False

        EffectEngine._deal_damage_to_target(kartya.nev, sebzes, cel, ellenfel, kontextus, jatekos)
        return True

    @staticmethod
    def _resolve_buff(kartya, jatekos, szoveg, kontextus):
        atk_bonusz = EffectEngine._extract_number(szoveg, [
            r'\+(\d+)\s*atk',
            r'kap\s+\+(\d+)\s*atk',
            r'(\d+)\s*atk-t\s+kap',
            r'\+(\d+)\s*tamadas',
            r'noveli\s+(\d+)\s*atk',
        ])
        hp_bonusz = EffectEngine._extract_number(szoveg, [
            r'\+(\d+)\s*(?:hp|eletero)',
            r'kap\s+\+(\d+)\s*(?:hp|eletero)',
            r'(\d+)\s*(?:hp|eletero)-t\s+kap',
            r'noveli\s+(\d+)\s*(?:hp|eletero)',
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
            r'gyogy(?:it|its|ul)?\s+(\d+)',
            r'(\d+)\s*(?:hp|eletero)\s+gyogyul',
            r'heal\s+(\d+)',
            r'visszatolt\s+(\d+)\s*(?:hp|eletero)',
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

        if EffectEngine._contains_any(
            szoveg,
            ["ideiglenes aura", "temporary aura", "rezonancia aura", "plusz aura", "extra aura"],
        ):
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
        tortent_valami |= EffectEngine._resolve_destroy(kartya, jatekos, ellenfel, szoveg, kontextus)
        tortent_valami |= EffectEngine._resolve_exhaust(kartya, jatekos, ellenfel, szoveg, kontextus)
        tortent_valami |= EffectEngine._resolve_buff(kartya, jatekos, szoveg, kontextus)
        tortent_valami |= EffectEngine._resolve_heal(kartya, jatekos, szoveg, kontextus)
        tortent_valami |= EffectEngine._resolve_temporary_aura(kartya, jatekos, szoveg, kontextus)
        tortent_valami |= EffectEngine._resolve_reactivate(kartya, jatekos, szoveg, kontextus)
        tortent_valami |= EffectEngine._resolve_resource_gain(kartya, jatekos, szoveg, kontextus)
        tortent_valami |= EffectEngine._resolve_provoke(kartya, jatekos, ellenfel, szoveg, kontextus)
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

        tortent_valami = False
        meghalt = False
        sebzes = EffectEngine._extract_number(szoveg, [
            r'(\d+)\s+(?:kozvetlen\s+)?sebzes',
            r'okoz\s+(\d+)\s+sebzest',
            r'sebez\s+(\d+)',
            r'(\d+)\s+damage',
        ])
        if sebzes > 0:
            naplo.ir(f"💥 Csapda: {jel.nev} -> {sebzes} sebzést okoz a támadónak!")
            meghalt = tamado_egyseg.serul(sebzes)
            tortent_valami = True

        atk_csokkentes = EffectEngine._extract_number(szoveg, [
            r'-(\d+)\s*atk',
            r'veszit\s+(\d+)\s*atk',
            r'csokkenti\s+(\d+)\s*atk',
        ])
        if atk_csokkentes > 0:
            tamado_egyseg.akt_tamadas = max(0, tamado_egyseg.akt_tamadas - atk_csokkentes)
            tortent_valami = True
            naplo.ir(f"🕸️ Csapda: {jel.nev} -> -{atk_csokkentes} ATK a támadónak")

        if "kimerit" in szoveg or "stun" in szoveg or "fagyaszt" in szoveg or "exhaust" in szoveg:
            tamado_egyseg.kimerult = True
            tortent_valami = True
            naplo.ir(f"🧊 Csapda: {jel.nev} -> a támadó kimerült")

        if "megsemmisit" in szoveg or "elpusztit" in szoveg or "pusztitsd el" in szoveg or "destroy" in szoveg:
            naplo.ir(f"☠️ Csapda: {jel.nev} -> a támadó megsemmisül")
            meghalt = True
            tortent_valami = True

        tortent_valami |= EffectEngine._resolve_draw(jel, vedo, szoveg, "Csapda")
        tortent_valami |= EffectEngine._resolve_heal(jel, vedo, szoveg, "Csapda")
        tortent_valami |= EffectEngine._resolve_buff(jel, vedo, szoveg, "Csapda")
        tortent_valami |= EffectEngine._resolve_temporary_aura(jel, vedo, szoveg, "Csapda")
        tortent_valami |= EffectEngine._resolve_reactivate(jel, vedo, szoveg, "Csapda")

        if not tortent_valami:
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
