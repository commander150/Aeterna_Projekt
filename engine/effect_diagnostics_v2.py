import re

from cards.resolver import resolve_card_handler
from engine.effects import EffectEngine
from engine.keyword_registry import KEYWORD_DEFINITIONS, KeywordRegistry
from utils.logger import naplo
from utils.text import normalize_lookup_text


PASSIVE_HINTS = (
    "[horizont]",
    "[zenit]",
    "amig",
    "while",
    "nem celozhato",
    "cannot be targeted",
    "rezonancia",
    "harmonize",
    "harmonizalas",
    "aegis",
    "oltalom",
    "ethereal",
    "legies",
    "celerity",
    "gyorsasag",
    "burst",
    "reakcio",
)

ACTIVE_HINTS = (
    "huzz",
    "draw",
    "okoz",
    "sebz",
    "destroy",
    "elpusztit",
    "megsemmisit",
    "kimerit",
    "stun",
    "fagyaszt",
    "kap",
    "letrehoz",
    "hozzaad",
    "visszavesz",
    "vedd vissza",
    "kezedbe",
    "zenitjebe",
    "zenitbe",
    "temetobol",
    "uressegbol",
    "nezz bele",
    "eldob",
    "visszalep",
    "tilos",
    "nem tamadhat",
    "nem blokkolhat",
)


def _has_known_keyword(text):
    return any(KeywordRegistry.has_keyword(text, key) for key in KEYWORD_DEFINITIONS)


def _classify_unresolved_effect(text):
    normalized = normalize_lookup_text(text)
    if not normalized or normalized == "-":
        return None

    if normalized in {"nincs kepessege", "nincs képessége", "no ability"}:
        return None

    has_keyword = _has_known_keyword(text)
    has_active = any(hint in normalized for hint in ACTIVE_HINTS)
    has_passive = any(hint in normalized for hint in PASSIVE_HINTS)

    if has_keyword and (has_passive and not has_active):
        return "passziv_only"
    if has_keyword and has_active:
        return "reszben_mukodo"
    return "tenylegesen_hianyzo"


def _record_if_needed(category, card, effect_text):
    allapot = _classify_unresolved_effect(effect_text)
    if allapot is None:
        return False
    EffectEngine._rogzit_fel_nem_oldott_effektet(category, card, effect_text, allapot)
    return True


def _trigger_on_play_with_diagnostics(kartya, jatekos, ellenfel):
    nyers_szoveg = kartya.kepesseg
    szoveg = EffectEngine._normalize_text(nyers_szoveg)
    if not szoveg or szoveg == "-":
        return None
    custom_result = resolve_card_handler(kartya, category="on_play", jatekos=jatekos, ellenfel=ellenfel)
    if custom_result.get("resolved"):
        return None

    sebzes_engedelyezett = (
        kartya.kartyatipus in ["Ige", "RituĂˇlĂ©", "Rituale"]
        or "riado" in szoveg
        or "clarion" in szoveg
    )

    tortent_valami = EffectEngine._resolve_common_effects(
        kartya, jatekos, ellenfel, szoveg, "Képesség", sebzes_engedelyezett
    )

    if not tortent_valami and _record_if_needed("on_play", kartya, nyers_szoveg):
        naplo.ir(f"⚠️ Képesség: {kartya.nev} aktiválódott, de nem volt ismert konkrét hatása")

    return None


def _trigger_on_trap_with_diagnostics(jel, tamado_egyseg, tamado, vedo):
    szoveg = EffectEngine._normalize_text(jel.kepesseg)
    if not szoveg or szoveg == "-":
        return False
    custom_result = resolve_card_handler(
        jel,
        category="trap",
        tamado_egyseg=tamado_egyseg,
        tamado=tamado,
        vedo=vedo,
    )
    if custom_result.get("resolved"):
        return custom_result

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
        naplo.ir(f"🗡️ Csapda: {jel.nev} -> -{atk_csokkentes} ATK a támadónak")

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

    if not tortent_valami and _record_if_needed("trap", jel, jel.kepesseg):
        naplo.ir(f"⚠️ Egyedi Csapda: {jel.nev} aktiválódott, de nem volt ismert konkrét hatása")

    return meghalt


def _trigger_on_burst_with_diagnostics(kartya, jatekos, ellenfel=None):
    szoveg = EffectEngine._normalize_text(kartya.kepesseg)
    if not szoveg or szoveg == "-":
        return False

    tortent_valami = EffectEngine._resolve_common_effects(
        kartya, jatekos, ellenfel, szoveg, "Burst", True
    )

    if not tortent_valami and _record_if_needed("burst", kartya, kartya.kepesseg):
        naplo.ir(f"✨ Burst: {kartya.nev} aktiválódott")

    return tortent_valami


def _trigger_on_death_with_diagnostics(kartya, jatekos, ellenfel=None):
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

    if not tortent_valami and _record_if_needed("death", kartya, death_text):
        naplo.ir(f"✨ Halál effekt: {kartya.nev} aktiválódott")

    return True


EffectEngine.trigger_on_play = staticmethod(_trigger_on_play_with_diagnostics)
EffectEngine.trigger_on_trap = staticmethod(_trigger_on_trap_with_diagnostics)
EffectEngine.trigger_on_burst = staticmethod(_trigger_on_burst_with_diagnostics)
EffectEngine.trigger_on_death = staticmethod(_trigger_on_death_with_diagnostics)
