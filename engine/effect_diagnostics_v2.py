import re

from cards.resolver import resolve_card_handler
from engine.effects import EffectEngine
from engine.keyword_registry import KEYWORD_DEFINITIONS, KeywordRegistry
from engine.structured_effects import (
    STRUCTURED_STATUS_DEFERRED,
    STRUCTURED_STATUS_FALLBACK_USED,
    STRUCTURED_STATUS_MISSING,
    STRUCTURED_STATUS_NOT_APPLICABLE,
    STRUCTURED_STATUS_NO_STRUCTURED,
    STRUCTURED_STATUS_PARTIAL,
    STRUCTURED_STATUS_RESOLVED,
    get_structured_status,
    is_passive_structured_card,
    resolve_structured_effect,
)
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
        return "passive_static_ignored"

    structured_status = get_structured_status(card)
    if structured_status in {"passive_static_ignored", "structured_partial", "structured_deferred"}:
        return structured_status

    has_keyword = bool(getattr(card, "keywords_normalized", [])) or _has_known_keyword(text)
    has_active = bool(getattr(card, "effect_tags_normalized", [])) or any(hint in normalized for hint in ACTIVE_HINTS)
    has_passive = has_keyword or any(hint in normalized for hint in PASSIVE_HINTS)

    if has_keyword and (has_passive and not has_active):
        return "passive_static_ignored"
    if has_active and getattr(card, "structured_data_available", False):
        return "structured_partial"
    return "missing_implementation"


def _record_structured_result(metric_status, category, card, effect_text, record_status=None):
    stats.rogzit_structured_kimenetet(metric_status)
    if record_status:
        EffectEngine._rogzit_fel_nem_oldott_effektet(category, card, effect_text, record_status)


def _run_structured(card, source_player, target_player=None, context=None):
    if not getattr(card, "structured_data_available", False):
        return {"status": STRUCTURED_STATUS_NO_STRUCTURED, "resolved": False, "mode": "no_structured"}
    stats.rogzit_structured_kimenetet("attempted")
    return resolve_structured_effect(card, source_player, target_player, context or {})


def _trigger_on_play_with_diagnostics(kartya, jatekos, ellenfel):
    nyers_szoveg = _effect_text(kartya)
    szoveg = EffectEngine._normalize_text(nyers_szoveg)
    if not szoveg or szoveg == "-":
        return None

    structured_result = _run_structured(kartya, jatekos, ellenfel, {"category": "on_play"})
    structured_status = structured_result.get("status")
    pending_partial = structured_status == STRUCTURED_STATUS_PARTIAL
    if structured_status == STRUCTURED_STATUS_RESOLVED:
        _record_structured_result("resolved", "on_play", kartya, nyers_szoveg)
        return None
    if structured_status == STRUCTURED_STATUS_DEFERRED:
        _record_structured_result("deferred", "on_play", kartya, nyers_szoveg, "structured_deferred")
        return None
    elif structured_status == "passive_static_ignored":
        _record_structured_result("passive", "on_play", kartya, nyers_szoveg, "passive_static_ignored")
        return None
    elif structured_status == STRUCTURED_STATUS_NOT_APPLICABLE:
        _record_structured_result("not_applicable", "on_play", kartya, nyers_szoveg)
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
        _record_structured_result("fallback", "on_play", kartya, nyers_szoveg, "fallback_text_resolved")
        return None

    if pending_partial:
        _record_structured_result("partial", "on_play", kartya, nyers_szoveg, "structured_partial")
        return None

    _record_structured_result("missing", "on_play", kartya, nyers_szoveg, "missing_implementation")
    status = _classify_unresolved_effect(kartya, nyers_szoveg)
    if status == "missing_implementation":
        naplo.ir(f"[UNRESOLVED] Kepesseg: {kartya.nev} aktivodott, de nem volt ismert konkret hatasa")

    return None


def _trigger_on_trap_with_diagnostics(jel, tamado_egyseg, tamado, vedo):
    szoveg = EffectEngine._normalize_text(_effect_text(jel))
    if not szoveg or szoveg == "-":
        return False

    structured_result = _run_structured(jel, vedo, tamado, {"category": "trap", "tamado_egyseg": tamado_egyseg, "tamado": tamado, "vedo": vedo})
    structured_status = structured_result.get("status")
    pending_partial = structured_status == STRUCTURED_STATUS_PARTIAL
    if structured_status == STRUCTURED_STATUS_RESOLVED:
        _record_structured_result("resolved", "trap", jel, _effect_text(jel))
        return structured_result
    if structured_status == STRUCTURED_STATUS_DEFERRED:
        _record_structured_result("deferred", "trap", jel, _effect_text(jel), "structured_deferred")
        return False
    elif structured_status == "passive_static_ignored":
        _record_structured_result("passive", "trap", jel, _effect_text(jel), "passive_static_ignored")
        return False
    elif structured_status == STRUCTURED_STATUS_NOT_APPLICABLE:
        _record_structured_result("not_applicable", "trap", jel, _effect_text(jel))
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
        _record_structured_result("fallback", "trap", jel, _effect_text(jel), "fallback_text_resolved")
        return meghalt

    if pending_partial:
        _record_structured_result("partial", "trap", jel, _effect_text(jel), "structured_partial")
        return meghalt

    _record_structured_result("missing", "trap", jel, _effect_text(jel), "missing_implementation")
    status = _classify_unresolved_effect(jel, _effect_text(jel))
    if status == "missing_implementation":
        naplo.ir(f"[UNRESOLVED] Egyedi Csapda: {jel.nev} aktivodott, de nem volt ismert konkret hatasa")

    return meghalt


def _trigger_on_burst_with_diagnostics(kartya, jatekos, ellenfel=None):
    szoveg = EffectEngine._normalize_text(_effect_text(kartya))
    if not szoveg or szoveg == "-":
        return False

    structured_result = _run_structured(kartya, jatekos, ellenfel, {"category": "burst"})
    structured_status = structured_result.get("status")
    pending_partial = structured_status == STRUCTURED_STATUS_PARTIAL
    if structured_status == STRUCTURED_STATUS_RESOLVED:
        _record_structured_result("resolved", "burst", kartya, _effect_text(kartya))
        return True
    if structured_status == STRUCTURED_STATUS_DEFERRED:
        _record_structured_result("deferred", "burst", kartya, _effect_text(kartya), "structured_deferred")
        return False
    elif structured_status == "passive_static_ignored":
        _record_structured_result("passive", "burst", kartya, _effect_text(kartya), "passive_static_ignored")
        return False
    elif structured_status == STRUCTURED_STATUS_NOT_APPLICABLE:
        _record_structured_result("not_applicable", "burst", kartya, _effect_text(kartya))
        return False

    custom_result = resolve_card_handler(kartya, category="burst", jatekos=jatekos, ellenfel=ellenfel)
    if custom_result.get("resolved"):
        return True

    tortent_valami = EffectEngine._resolve_common_effects(
        kartya, jatekos, ellenfel, szoveg, "Burst", True
    )

    if tortent_valami:
        _record_structured_result("fallback", "burst", kartya, _effect_text(kartya), "fallback_text_resolved")
        return True

    if pending_partial:
        _record_structured_result("partial", "burst", kartya, _effect_text(kartya), "structured_partial")
        return False

    _record_structured_result("missing", "burst", kartya, _effect_text(kartya), "missing_implementation")
    return False


def _trigger_on_death_with_diagnostics(kartya, jatekos, ellenfel=None):
    szoveg = EffectEngine._normalize_text(_effect_text(kartya))
    if not szoveg or szoveg == "-":
        return False

    structured_result = _run_structured(kartya, jatekos, ellenfel, {"category": "death"})
    structured_status = structured_result.get("status")
    pending_partial = structured_status == STRUCTURED_STATUS_PARTIAL
    if structured_status == STRUCTURED_STATUS_RESOLVED:
        _record_structured_result("resolved", "death", kartya, _effect_text(kartya))
        return True
    if structured_status == STRUCTURED_STATUS_DEFERRED:
        _record_structured_result("deferred", "death", kartya, _effect_text(kartya), "structured_deferred")
        return False
    elif structured_status == "passive_static_ignored":
        _record_structured_result("passive", "death", kartya, _effect_text(kartya), "passive_static_ignored")
        return False
    elif structured_status == STRUCTURED_STATUS_NOT_APPLICABLE:
        _record_structured_result("not_applicable", "death", kartya, _effect_text(kartya))
        return False

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
        _record_structured_result("fallback", "death", kartya, death_text, "fallback_text_resolved")
        return True

    if pending_partial:
        _record_structured_result("partial", "death", kartya, death_text, "structured_partial")
        return True

    _record_structured_result("missing", "death", kartya, death_text, "missing_implementation")
    status = _classify_unresolved_effect(kartya, death_text)
    if status == "missing_implementation":
        naplo.ir(f"Halal effekt: {kartya.nev} aktivodott")

    return True


EffectEngine.trigger_on_play = staticmethod(_trigger_on_play_with_diagnostics)
EffectEngine.trigger_on_trap = staticmethod(_trigger_on_trap_with_diagnostics)
EffectEngine.trigger_on_burst = staticmethod(_trigger_on_burst_with_diagnostics)
EffectEngine.trigger_on_death = staticmethod(_trigger_on_death_with_diagnostics)
