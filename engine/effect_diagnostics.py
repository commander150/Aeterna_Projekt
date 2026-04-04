import re

from engine.effects import EffectEngine
from utils.logger import naplo


def _trigger_on_play_with_diagnostics(kartya, jatekos, ellenfel):
    nyers_szoveg = kartya.kepesseg
    szoveg = EffectEngine._normalize_text(nyers_szoveg)
    if not szoveg or szoveg == "-":
        return None

    sebzes_engedelyezett = (
        kartya.kartyatipus in ["Ige", "Rituálé"]
        or "riado" in szoveg
        or "clarion" in szoveg
    )

    tortent_valami = EffectEngine._resolve_common_effects(
        kartya, jatekos, ellenfel, szoveg, "Képesség", sebzes_engedelyezett
    )

    if not tortent_valami:
        EffectEngine._rogzit_fel_nem_oldott_effektet("on_play", kartya, nyers_szoveg)
        naplo.ir(f"âš ď¸Ź Képesség: {kartya.nev} aktiválodott, de nem volt ismert konkrét hatása")

    return None


def _trigger_on_trap_with_diagnostics(jel, tamado_egyseg, tamado, vedo):
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
        naplo.ir(f"đź’Ą Csapda: {jel.nev} -> {sebzes} sebzést okoz a támadónak!")
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
        naplo.ir(f"đź•¸ď¸Ź Csapda: {jel.nev} -> -{atk_csokkentes} ATK a támadónak")

    if "kimerit" in szoveg or "stun" in szoveg or "fagyaszt" in szoveg or "exhaust" in szoveg:
        tamado_egyseg.kimerult = True
        tortent_valami = True
        naplo.ir(f"đź§Š Csapda: {jel.nev} -> a tĂˇmadĂł kimerĂĽlt")

    if "megsemmisit" in szoveg or "elpusztit" in szoveg or "pusztitsd el" in szoveg or "destroy" in szoveg:
        naplo.ir(f"â ď¸Ź Csapda: {jel.nev} -> a tĂˇmadĂł megsemmisĂĽl")
        meghalt = True
        tortent_valami = True

    tortent_valami |= EffectEngine._resolve_draw(jel, vedo, szoveg, "Csapda")
    tortent_valami |= EffectEngine._resolve_heal(jel, vedo, szoveg, "Csapda")
    tortent_valami |= EffectEngine._resolve_buff(jel, vedo, szoveg, "Csapda")
    tortent_valami |= EffectEngine._resolve_temporary_aura(jel, vedo, szoveg, "Csapda")
    tortent_valami |= EffectEngine._resolve_reactivate(jel, vedo, szoveg, "Csapda")

    if not tortent_valami:
        EffectEngine._rogzit_fel_nem_oldott_effektet("trap", jel, jel.kepesseg)
        naplo.ir(f"âš ď¸Ź Egyedi Csapda: {jel.nev} aktivĂˇlĂłdott, de nem volt ismert konkrĂ©t hatĂˇsa")

    return meghalt


def _trigger_on_burst_with_diagnostics(kartya, jatekos, ellenfel=None):
    szoveg = EffectEngine._normalize_text(kartya.kepesseg)
    if not szoveg or szoveg == "-":
        return False

    tortent_valami = EffectEngine._resolve_common_effects(
        kartya, jatekos, ellenfel, szoveg, "Burst", True
    )

    if not tortent_valami:
        EffectEngine._rogzit_fel_nem_oldott_effektet("burst", kartya, kartya.kepesseg)
        naplo.ir(f"âś¨ Burst: {kartya.nev} aktivĂˇlĂłdott")

    return tortent_valami


def _trigger_on_death_with_diagnostics(kartya, jatekos, ellenfel=None):
    szoveg = EffectEngine._normalize_text(getattr(kartya, "kepesseg", ""))
    if not szoveg or szoveg == "-":
        return False

    match = re.search(r'(?:visszhang|echo)\s*[:\-]?\s*(.+)', szoveg)
    if not match:
        return False

    death_text = match.group(1).strip()
    naplo.ir(f"âś¨ HalĂˇl effekt: {kartya.nev} (Echo/Visszhang)")

    if not death_text:
        return True

    tortent_valami = EffectEngine._resolve_common_effects(
        kartya, jatekos, ellenfel, death_text, "HalĂˇl effekt", True
    )

    if not tortent_valami:
        EffectEngine._rogzit_fel_nem_oldott_effektet("death", kartya, death_text)
        naplo.ir(f"âś¨ HalĂˇl effekt: {kartya.nev} aktivĂˇlĂłdott")

    return True


EffectEngine.trigger_on_play = staticmethod(_trigger_on_play_with_diagnostics)
EffectEngine.trigger_on_trap = staticmethod(_trigger_on_trap_with_diagnostics)
EffectEngine.trigger_on_burst = staticmethod(_trigger_on_burst_with_diagnostics)
EffectEngine.trigger_on_death = staticmethod(_trigger_on_death_with_diagnostics)
