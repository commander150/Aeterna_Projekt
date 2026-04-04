from engine.effects_expansions import handle_expansion_gate
from engine.triggers import trigger_engine
from utils.text import normalize_lookup_text

from cards.priority_handlers import (
    handle_a_gyenge_elhullik,
    handle_a_hulladektelep,
    can_activate_hamis_arany,
    can_activate_hamis_bizonyitek,
    can_activate_hamis_halal,
    can_activate_hamis_igeret,
    can_activate_kereskedelmi_embargo,
    can_activate_angyali_beavatkozas,
    can_activate_varatlan_erosites,
    handle_alvilagi_kapcsolatok,
    handle_angyali_beavatkozas,
    handle_az_orok_elet_temploma,
    handle_a_vilagok_keresztezodese,
    handle_csapda_a_fustben,
    handle_csapdaallito,
    handle_felderito_bagoly,
    handle_hamis_arany,
    handle_hamis_igeret,
    handle_hamis_halal,
    handle_informacio_vasarlas,
    handle_kereskedelmi_embargo,
    handle_kove_valas,
    handle_legaramlat_magus,
    handle_megtisztulas,
    handle_rendszerfrissites,
    on_destroyed,
    handle_varatlan_erosites,
    on_awakening_phase,
    resolve_combat_lethal_trap,
    resolve_spell_redirect_trap,
)


ON_PLAY_HANDLERS = {
    "felderito bagoly": handle_felderito_bagoly,
    "legaramlat-magus": handle_legaramlat_magus,
    "a vilagok keresztezodese": handle_a_vilagok_keresztezodese,
    "csapdaallito": handle_csapdaallito,
    "kove valas": handle_kove_valas,
    "megtisztulas": handle_megtisztulas,
    "a hulladektelep": handle_a_hulladektelep,
    "alvilagi kapcsolatok": handle_alvilagi_kapcsolatok,
    "az orok elet temploma": handle_az_orok_elet_temploma,
    "informacio-vasarlas": handle_informacio_vasarlas,
    "rendszerfrissites": handle_rendszerfrissites,
    "a gyenge elhullik": handle_a_gyenge_elhullik,
}

TRAP_HANDLERS = {
    "varatlan erosites": handle_varatlan_erosites,
    "hamis arany": handle_hamis_arany,
}

SUMMON_TRAP_HANDLERS = {
    "csapda a fustben": handle_csapda_a_fustben,
    "hamis igeret": handle_hamis_igeret,
    "kereskedelmi embargo": handle_kereskedelmi_embargo,
}

TRAP_PREVIEW_HANDLERS = {
    "varatlan erosites": can_activate_varatlan_erosites,
    "hamis arany": can_activate_hamis_arany,
    "hamis igeret": can_activate_hamis_igeret,
    "kereskedelmi embargo": can_activate_kereskedelmi_embargo,
    "angyali beavatkozas": can_activate_angyali_beavatkozas,
    "hamis bizonyitek": can_activate_hamis_bizonyitek,
    "hamis halal": can_activate_hamis_halal,
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


def resolve_spell_cast_trap(card, **context):
    return resolve_card_handler(card, category="trap", **context)


def resolve_lethal_trap(**context):
    return resolve_combat_lethal_trap(**context)


def resolve_spell_redirect(**context):
    return resolve_spell_redirect_trap(**context)


trigger_engine.register("on_awakening_phase", on_awakening_phase)
trigger_engine.register("on_destroyed", on_destroyed)
