import re

from cards.resolver import has_card_handler, resolve_card_handler
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

_INSTALLED = False


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

    if "nincs kepessege" in normalized or "no ability" in normalized:
        return None

    if is_passive_structured_card(card):
        return "passive_static_ignored"

    structured_status = get_structured_status(card)
    if structured_status in {
        "passive_static_ignored",
        "passive_static_applied",
        "static_not_explicitly_simulated",
        "structured_partial",
        "structured_deferred",
    }:
        return structured_status

    has_keyword = bool(getattr(card, "keywords_normalized", [])) or _has_known_keyword(text)
    has_active = bool(getattr(card, "effect_tags_normalized", [])) or any(hint in normalized for hint in ACTIVE_HINTS)
    has_passive = has_keyword or any(hint in normalized for hint in PASSIVE_HINTS)

    if has_keyword and (has_passive and not has_active):
        return "static_not_explicitly_simulated"
    if has_active and getattr(card, "structured_data_available", False):
        return "structured_partial"
    return "missing_implementation"


def _record_structured_result(metric_status, category, card, effect_text, record_status=None):
    stats.rogzit_structured_kimenetet(metric_status)
    if record_status:
        stats.rogzit_effekt_kimenetet(category, getattr(card, "nev", "Ismeretlen lap"), effect_text, record_status)


def _record_runtime_result(category, card, effect_text, status, metric=None):
    if metric:
        stats.rogzit_structured_kimenetet(metric)
    stats.rogzit_effekt_kimenetet(category, getattr(card, "nev", "Ismeretlen lap"), effect_text, status)


def _run_structured(card, source_player, target_player=None, context=None):
    if not getattr(card, "structured_data_available", False):
        return {"status": STRUCTURED_STATUS_NO_STRUCTURED, "resolved": False, "mode": "no_structured"}
    stats.rogzit_structured_kimenetet("attempted")
    return resolve_structured_effect(card, source_player, target_player, context or {})


def _trigger_on_play_with_diagnostics(kartya, jatekos, ellenfel, default_handler=None):
    nyers_szoveg = _effect_text(kartya)
    szoveg = EffectEngine._normalize_text(nyers_szoveg)
    if not szoveg or szoveg == "-":
        return None

    if has_card_handler(kartya, "on_play"):
        custom_result = resolve_card_handler(kartya, category="on_play", jatekos=jatekos, ellenfel=ellenfel)
        if custom_result.get("resolved"):
            _record_runtime_result("on_play", kartya, nyers_szoveg, "runtime_supported", "runtime_supported")
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
        _record_runtime_result("on_play", kartya, nyers_szoveg, "runtime_supported", "runtime_supported")
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
        _record_runtime_result("on_play", kartya, nyers_szoveg, "fallback_text_resolved", "fallback")
        return None

    if pending_partial:
        _record_structured_result("partial", "on_play", kartya, nyers_szoveg, "structured_partial")
        return None

    _record_runtime_result("on_play", kartya, nyers_szoveg, "missing_implementation", "missing")
    status = _classify_unresolved_effect(kartya, nyers_szoveg)
    if status == "missing_implementation":
        naplo.ir(f"[UNRESOLVED] Kepesseg: {kartya.nev} aktivodott, de nem volt ismert konkret hatasa")

    return None


def _trigger_on_trap_with_diagnostics(jel, tamado_egyseg, tamado, vedo, default_handler=None):
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
        if custom_result.get("consume_trap") and not any(
            custom_result.get(flag) for flag in ("stop_attack", "continue_attack", "prevented_death", "redirected_target", "cancelled_spell", "destroy_summoned")
        ):
            _record_runtime_result("trap", jel, _effect_text(jel), "trap_consumed_only", "trap_consumed_only")
        elif custom_result.get("partial"):
            _record_runtime_result("trap", jel, _effect_text(jel), "trap_partial", "trap_partial")
        else:
            _record_runtime_result("trap", jel, _effect_text(jel), "trap_resolved", "trap_resolved")
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
        _record_runtime_result("trap", jel, _effect_text(jel), "fallback_text_resolved", "fallback")
        return meghalt

    if pending_partial:
        _record_runtime_result("trap", jel, _effect_text(jel), "trap_partial", "trap_partial")
        return meghalt

    _record_runtime_result("trap", jel, _effect_text(jel), "trap_missing", "trap_missing")
    status = _classify_unresolved_effect(jel, _effect_text(jel))
    if status in {"missing_implementation", "trap_missing"}:
        naplo.ir(f"[UNRESOLVED] Egyedi Csapda: {jel.nev} aktivodott, de nem volt ismert konkret hatasa")

    return meghalt


def _trigger_on_burst_with_diagnostics(kartya, jatekos, ellenfel=None, default_handler=None):
    szoveg = EffectEngine._normalize_text(_effect_text(kartya))
    if not szoveg or szoveg == "-":
        return False

    if has_card_handler(kartya, "burst"):
        custom_result = resolve_card_handler(kartya, category="burst", jatekos=jatekos, ellenfel=ellenfel)
        if custom_result.get("resolved"):
            _record_runtime_result("burst", kartya, _effect_text(kartya), "runtime_supported", "runtime_supported")
            return True

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
        _record_runtime_result("burst", kartya, _effect_text(kartya), "runtime_supported", "runtime_supported")
        return True

    tortent_valami = EffectEngine._resolve_common_effects(
        kartya, jatekos, ellenfel, szoveg, "Burst", True
    )

    if tortent_valami:
        _record_runtime_result("burst", kartya, _effect_text(kartya), "fallback_text_resolved", "fallback")
        return True

    if pending_partial:
        _record_structured_result("partial", "burst", kartya, _effect_text(kartya), "structured_partial")
        return False

    _record_runtime_result("burst", kartya, _effect_text(kartya), "missing_implementation", "missing")
    return False


def _trigger_on_death_with_diagnostics(kartya, jatekos, ellenfel=None, default_handler=None):
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
        _record_runtime_result("death", kartya, death_text, "legacy_supported", "legacy_supported")
        return True

    if pending_partial:
        _record_structured_result("partial", "death", kartya, death_text, "structured_partial")
        return True

    _record_runtime_result("death", kartya, death_text, "missing_implementation", "missing")
    status = _classify_unresolved_effect(kartya, death_text)
    if status == "missing_implementation":
        naplo.ir(f"Halal effekt: {kartya.nev} aktivodott")

    return True


def install_effect_diagnostics():
    global _INSTALLED
    if _INSTALLED:
        return False

    EffectEngine.install_trigger_adapter("on_play", _trigger_on_play_with_diagnostics)
    EffectEngine.install_trigger_adapter("trap", _trigger_on_trap_with_diagnostics)
    EffectEngine.install_trigger_adapter("burst", _trigger_on_burst_with_diagnostics)
    EffectEngine.install_trigger_adapter("death", _trigger_on_death_with_diagnostics)
    _INSTALLED = True
    return True


def is_effect_diagnostics_installed():
    return _INSTALLED
