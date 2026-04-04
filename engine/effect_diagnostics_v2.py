import re

from cards.resolver import resolve_card_handler
from engine.effects import EffectEngine
from engine.keyword_registry import KEYWORD_DEFINITIONS, KeywordRegistry
from engine.structured_effects import get_structured_status, is_passive_structured_card, resolve_structured_effect
from stats.analyzer import stats
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


def _effect_text(card):
    return getattr(card, "canonical_text", "") or getattr(card, "kepesseg", "")


def _has_known_keyword(text):
    return any(KeywordRegistry.has_keyword(text, key) for key in KEYWORD_DEFINITIONS)


def _classify_unresolved_effect(card, text):
    normalized = normalize_lookup_text(text)
    if not normalized or normalized == "-":
        return None

    if normalized in {"nincs kepessege", "no ability"}:
        return None

    if is_passive_structured_card(card):
        return "passziv_kulcsszo"

    structured_status = get_structured_status(card)
    if structured_status in {"passziv_kulcsszo", "structured_partial"}:
        return structured_status

    has_keyword = bool(getattr(card, "keywords_normalized", [])) or _has_known_keyword(text)
    has_active = bool(getattr(card, "effect_tags_normalized", [])) or any(hint in normalized for hint in ACTIVE_HINTS)
    has_passive = has_keyword or any(hint in normalized for hint in PASSIVE_HINTS)

    if has_keyword and (has_passive and not has_active):
        return "passziv_kulcsszo"
    if has_active and getattr(card, "structured_data_available", False):
        return "structured_partial"
    return "missing_implementation"


def _record_if_needed(category, card, effect_text):
    status = _classify_unresolved_effect(card, effect_text)
    if status is None:
        return False, None
    EffectEngine._rogzit_fel_nem_oldott_effektet(category, card, effect_text, status)
    return True, status


def _run_structured(card, source_player, target_player=None, context=None):
    if not getattr(card, "structured_data_available", False):
        return {"resolved": False, "mode": "no_structured"}
    stats.rogzit_structured_kimenetet("attempted")
    result = resolve_structured_effect(card, source_player, target_player, context or {})
    if result.get("resolved") and not result.get("partial"):
        stats.rogzit_structured_kimenetet("resolved")
    elif result.get("partial"):
        stats.rogzit_structured_kimenetet("partial")
    return result


def _trigger_on_play_with_diagnostics(kartya, jatekos, ellenfel):
    nyers_szoveg = _effect_text(kartya)
    szoveg = EffectEngine._normalize_text(nyers_szoveg)
    if not szoveg or szoveg == "-":
        return None

    structured_result = _run_structured(kartya, jatekos, ellenfel, {"category": "on_play"})
    if structured_result.get("resolved") and not structured_result.get("partial"):
        return None

    custom_result = resolve_card_handler(kartya, category="on_play", jatekos=jatekos, ellenfel=ellenfel)
    if custom_result.get("resolved"):
        return None

    sebzes_engedelyezett = (
        kartya.kartyatipus in ["Ige", "Rituale", "Rituale"]
        or "riado" in szoveg
        or "clarion" in szoveg
    )

    tortent_valami = EffectEngine._resolve_common_effects(
        kartya, jatekos, ellenfel, szoveg, "Kepesseg", sebzes_engedelyezett
    )

    if tortent_valami:
        stats.rogzit_structured_kimenetet("fallback")
        return None

    stats.rogzit_structured_kimenetet("unresolved")
    recorded, status = _record_if_needed("on_play", kartya, nyers_szoveg)
    if recorded and status == "missing_implementation":
        naplo.ir(f"[UNRESOLVED] Kepesseg: {kartya.nev} aktivodott, de nem volt ismert konkret hatasa")

    return None


def _trigger_on_trap_with_diagnostics(jel, tamado_egyseg, tamado, vedo):
    szoveg = EffectEngine._normalize_text(_effect_text(jel))
    if not szoveg or szoveg == "-":
        return False

    structured_result = _run_structured(jel, vedo, tamado, {"category": "trap", "tamado_egyseg": tamado_egyseg, "tamado": tamado, "vedo": vedo})
    if structured_result.get("resolved") and not structured_result.get("partial"):
        return structured_result

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

    if "kimerit" in szoveg or "stun" in szoveg or "fagyaszt" in szoveg or "exhaust" in szoveg:
        tamado_egyseg.kimerult = True
        tortent_valami = True

    if "megsemmisit" in szoveg or "elpusztit" in szoveg or "pusztitsd el" in szoveg or "destroy" in szoveg:
        meghalt = True
        tortent_valami = True

    tortent_valami |= EffectEngine._resolve_draw(jel, vedo, szoveg, "Csapda")
    tortent_valami |= EffectEngine._resolve_heal(jel, vedo, szoveg, "Csapda")
    tortent_valami |= EffectEngine._resolve_buff(jel, vedo, szoveg, "Csapda")
    tortent_valami |= EffectEngine._resolve_temporary_aura(jel, vedo, szoveg, "Csapda")
    tortent_valami |= EffectEngine._resolve_reactivate(jel, vedo, szoveg, "Csapda")

    if tortent_valami:
        stats.rogzit_structured_kimenetet("fallback")
        return meghalt

    stats.rogzit_structured_kimenetet("unresolved")
    recorded, status = _record_if_needed("trap", jel, _effect_text(jel))
    if recorded and status == "missing_implementation":
        naplo.ir(f"[UNRESOLVED] Egyedi Csapda: {jel.nev} aktivodott, de nem volt ismert konkret hatasa")

    return meghalt


def _trigger_on_burst_with_diagnostics(kartya, jatekos, ellenfel=None):
    szoveg = EffectEngine._normalize_text(_effect_text(kartya))
    if not szoveg or szoveg == "-":
        return False

    structured_result = _run_structured(kartya, jatekos, ellenfel, {"category": "burst"})
    if structured_result.get("resolved") and not structured_result.get("partial"):
        return True

    custom_result = resolve_card_handler(kartya, category="burst", jatekos=jatekos, ellenfel=ellenfel)
    if custom_result.get("resolved"):
        return True

    tortent_valami = EffectEngine._resolve_common_effects(
        kartya, jatekos, ellenfel, szoveg, "Burst", True
    )

    if tortent_valami:
        stats.rogzit_structured_kimenetet("fallback")
        return True

    stats.rogzit_structured_kimenetet("unresolved")
    _record_if_needed("burst", kartya, _effect_text(kartya))
    return False


def _trigger_on_death_with_diagnostics(kartya, jatekos, ellenfel=None):
    szoveg = EffectEngine._normalize_text(_effect_text(kartya))
    if not szoveg or szoveg == "-":
        return False

    structured_result = _run_structured(kartya, jatekos, ellenfel, {"category": "death"})
    if structured_result.get("resolved") and not structured_result.get("partial"):
        return True

    match = re.search(r'(?:visszhang|echo)\s*[:\-]?\s*(.+)', szoveg)
    if not match:
        return False

    death_text = match.group(1).strip()
    naplo.ir(f"Halal effekt: {kartya.nev} (Echo/Visszhang)")

    if not death_text:
        return True

    tortent_valami = EffectEngine._resolve_common_effects(
        kartya, jatekos, ellenfel, death_text, "Halal effekt", True
    )

    if tortent_valami:
        stats.rogzit_structured_kimenetet("fallback")
        return True

    stats.rogzit_structured_kimenetet("unresolved")
    recorded, status = _record_if_needed("death", kartya, death_text)
    if recorded and status == "missing_implementation":
        naplo.ir(f"Halal effekt: {kartya.nev} aktivodott")

    return True


EffectEngine.trigger_on_play = staticmethod(_trigger_on_play_with_diagnostics)
EffectEngine.trigger_on_trap = staticmethod(_trigger_on_trap_with_diagnostics)
EffectEngine.trigger_on_burst = staticmethod(_trigger_on_burst_with_diagnostics)
EffectEngine.trigger_on_death = staticmethod(_trigger_on_death_with_diagnostics)
