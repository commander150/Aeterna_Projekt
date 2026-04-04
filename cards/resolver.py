from engine.effects_expansions import handle_expansion_gate
from engine.triggers import trigger_engine
from utils.text import normalize_lookup_text

from cards.priority_handlers import (
    can_activate_varatlan_erosites,
    handle_a_vilagok_keresztezodese,
    handle_csapda_a_fustben,
    handle_csapdaallito,
    handle_felderito_bagoly,
    handle_kove_valas,
    handle_legaramlat_magus,
    handle_megtisztulas,
    handle_varatlan_erosites,
    on_awakening_phase,
)


ON_PLAY_HANDLERS = {
    "felderito bagoly": handle_felderito_bagoly,
    "legaramlat-magus": handle_legaramlat_magus,
    "a vilagok keresztezodese": handle_a_vilagok_keresztezodese,
    "csapdaallito": handle_csapdaallito,
    "kove valas": handle_kove_valas,
    "megtisztulas": handle_megtisztulas,
}

TRAP_HANDLERS = {
    "varatlan erosites": handle_varatlan_erosites,
}

SUMMON_TRAP_HANDLERS = {
    "csapda a fustben": handle_csapda_a_fustben,
}

TRAP_PREVIEW_HANDLERS = {
    "varatlan erosites": can_activate_varatlan_erosites,
}


def _handler_key(card):
    return normalize_lookup_text(getattr(card, "nev", ""))


def resolve_card_handler(card, category="on_play", **context):
    if handle_expansion_gate(getattr(card, "nev", "Ismeretlen lap"), getattr(card, "kepesseg", "")):
        return {"status": "skipped", "category": category, "resolved": True}

    key = _handler_key(card)
    if category == "on_play":
        handler = ON_PLAY_HANDLERS.get(key)
    elif category == "trap":
        handler = TRAP_HANDLERS.get(key)
    elif category == "summon_trap":
        handler = SUMMON_TRAP_HANDLERS.get(key)
    else:
        handler = None

    if handler is None:
        return {"status": "unhandled", "category": category, "resolved": False}

    result = handler(card, **context) or {}
    result.setdefault("status", "handled")
    result.setdefault("category", category)
    result.setdefault("resolved", True)
    return result


def can_activate_trap(card, **context):
    preview = TRAP_PREVIEW_HANDLERS.get(_handler_key(card))
    if preview is None:
        return True
    return bool(preview(card, **context))


trigger_engine.register("on_awakening_phase", on_awakening_phase)
