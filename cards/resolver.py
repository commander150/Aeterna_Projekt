from engine.effects_expansions import handle_expansion_gate
from engine.triggers import trigger_engine
from utils.text import normalize_lookup_text

from cards.priority_handlers import (
    handle_a_gyenge_elhullik,
    handle_a_hulladektelep,
    handle_a_melyseg_szeme,
    handle_a_tomegtermeles_gyara,
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
    handle_csaloka_hullam,
    handle_csapda_a_fustben,
    handle_csapdaallito,
    handle_egi_emeles,
    handle_felderito_bagoly,
    handle_goznyomasos_kiloves,
    handle_gyar_felugyelo,
    handle_hamis_arany,
    handle_hamis_igeret,
    handle_hamis_halal,
    handle_informacio_vasarlas,
    handle_kereskedelmi_embargo,
    handle_kove_valas,
    handle_lathatatlan_fal,
    handle_legaramlat_magus,
    handle_kod_alak,
    handle_lopakodo_felcser_dron,
    handle_sivatagi_kem,
    handle_tengeri_delibab,
    handle_tuzeso,
    handle_univerzalis_csere,
    handle_viharos_menekules,
    handle_visszahivas_az_uressegbol,
    handle_megtisztulas,
    handle_rendszerfrissites,
    on_destroyed,
    handle_varatlan_erosites,
    on_awakening_phase,
    on_spell_targeted_priority,
    on_summon_priority,
    on_turn_end_priority,
    resolve_combat_lethal_trap,
    resolve_spell_redirect_trap,
    handle_sivatagi_kem_pecset_sebzes,
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
    "tuzeso": handle_tuzeso,
    "goznyomasos kiloves": handle_goznyomasos_kiloves,
    "visszahivas az uressegbol": handle_visszahivas_az_uressegbol,
    "gyar-felugyelo": handle_gyar_felugyelo,
    "a tomegtermeles gyara": handle_a_tomegtermeles_gyara,
    "egi emeles": handle_egi_emeles,
    "tengeri delibab": handle_tengeri_delibab,
    "viharos menekules": handle_viharos_menekules,
    "univerzalis csere": handle_univerzalis_csere,
    "kod-alak": handle_kod_alak,
    "lopakodo felcser-dron": handle_lopakodo_felcser_dron,
    "sivatagi kem": handle_sivatagi_kem,
}

TRAP_HANDLERS = {
    "varatlan erosites": handle_varatlan_erosites,
    "hamis arany": handle_hamis_arany,
    "lathatatlan fal": handle_lathatatlan_fal,
}

SUMMON_TRAP_HANDLERS = {
    "csapda a fustben": handle_csapda_a_fustben,
    "hamis igeret": handle_hamis_igeret,
    "kereskedelmi embargo": handle_kereskedelmi_embargo,
    "a melyseg szeme": handle_a_melyseg_szeme,
}

TRAP_PREVIEW_HANDLERS = {
    "varatlan erosites": can_activate_varatlan_erosites,
    "hamis arany": can_activate_hamis_arany,
    "hamis igeret": can_activate_hamis_igeret,
    "kereskedelmi embargo": can_activate_kereskedelmi_embargo,
    "angyali beavatkozas": can_activate_angyali_beavatkozas,
    "hamis bizonyitek": can_activate_hamis_bizonyitek,
    "hamis halal": can_activate_hamis_halal,
    "lathatatlan fal": lambda card, target_kind=None, **_: target_kind == "seal",
    "tulhevult kazan": lambda *_, **__: False,
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
trigger_engine.register("on_summon", on_summon_priority)
trigger_engine.register("on_spell_targeted", on_spell_targeted_priority)
trigger_engine.register("on_turn_end", on_turn_end_priority)
