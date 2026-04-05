from engine.effects_expansions import handle_expansion_gate
from engine.triggers import trigger_engine
from utils.text import normalize_lookup_text

from cards.priority_handlers import (
    handle_a_gyenge_elhullik,
    handle_a_valtozo_sziget,
    handle_a_zatony_eneke,
    handle_a_feny_neve,
    handle_a_feny_utja,
    handle_aeterna_aldasa,
    handle_apaly_es_dagaly,
    handle_a_hulladektelep,
    handle_a_melyseg_szeme,
    handle_a_tomegtermeles_gyara,
    handle_a_termeszet_szava,
    can_activate_hamis_arany,
    can_activate_hamis_bizonyitek,
    can_activate_hamis_halal,
    can_activate_hamis_igeret,
    can_activate_kereskedelmi_embargo,
    can_activate_angyali_beavatkozas,
    can_activate_varatlan_erosites,
    handle_alvilagi_kapcsolatok,
    handle_angyali_beavatkozas,
    handle_atkozott_orveny,
    handle_az_orok_elet_temploma,
    handle_a_vilagok_keresztezodese,
    handle_benito_fagy,
    handle_buborek_pajzs,
    handle_langok_vedelme,
    handle_folyekony_pancel,
    handle_vedelmezo_burok,
    can_activate_atkozott_orveny,
    can_activate_benito_fagy,
    handle_csuszos_talaj,
    can_activate_csuszos_talaj,
    handle_csaloka_hullam,
    handle_csapda_a_fustben,
    handle_csapdaallito,
    handle_fenykard_csapas,
    handle_goblin_taktika,
    handle_egi_emeles,
    handle_fustbomba,
    handle_kraken_idomar,
    handle_felderito_bagoly,
    handle_lelekmentes,
    handle_goznyomasos_kiloves,
    handle_melytengeri_nyomas,
    handle_pusztito_roham,
    handle_vakito_fust,
    handle_nagy_aramlas,
    handle_onfelaldozo_esku,
    handle_ork_tabor,
    handle_orveny_nyeles,
    can_activate_orveny_nyeles,
    handle_gyar_felugyelo,
    handle_hamis_arany,
    handle_hamis_igeret,
    handle_hamis_halal,
    handle_hirtelen_dagaly,
    handle_informacio_vasarlas,
    handle_isteni_erintes,
    handle_kereskedelmi_embargo,
    handle_kagylo_csapda,
    handle_koborlo_lelek,
    handle_kove_valas,
    handle_keresztes_hadjarat,
    handle_kitero_manover,
    handle_kodbe_vesz,
    handle_lathatatlan_fal,
    handle_legaramlat_magus,
    handle_langnyelv_adeptus,
    handle_langnyelvek_tanca,
    handle_magma_elemental,
    handle_martirok_vedelme,
    handle_megtorlo_feny,
    handle_meglepetesszeru_ellenakcio,
    handle_megvesztegetes,
    handle_varatlan_gyulladas,
    handle_hamuba_fojtas,
    handle_kod_alak,
    handle_lopakodo_felcser_dron,
    handle_szentjanosbogar_raj,
    handle_szent_lang_inkvizitor,
    handle_surgeto_hullam,
    handle_vakito_ragyogas,
    handle_vakito_seregek,
    handle_vakito_szikra,
    handle_vakito_visszavagas,
    handle_vadon_szeme_ijasz,
    handle_sikatori_zsebtolvaj,
    handle_sirba_teres,
    handle_varatlan_apaly,
    handle_viharos_ellencsapas,
    handle_vegzetes_lepes,
    handle_sivatagi_kem,
    handle_vizeses_golem,
    handle_szegecsvihar,
    handle_uresseg_kutato,
    handle_zart_sorkepzes,
    handle_zatony_felderito,
    handle_viz_alatti_borton,
    handle_tengeri_delibab,
    handle_tornado_csapda,
    handle_tukrozodo_remeny,
    handle_tuzeso,
    handle_ujjaszuletes_fenye,
    handle_univerzalis_csere,
    handle_vamszedo_pont,
    handle_gyorsitott_menet,
    handle_viharos_menekules,
    handle_visszahivas_az_uressegbol,
    handle_megtisztulas,
    handle_rendszerfrissites,
    handle_eletado_fopap,
    on_damage_taken_priority,
    on_destroyed,
    handle_varatlan_erosites,
    on_awakening_phase,
    on_spell_targeted_priority,
    on_summon_priority,
    on_turn_end_priority,
    resolve_combat_lethal_trap,
    resolve_spell_redirect_trap,
    handle_sivatagi_kem_pecset_sebzes,
    can_activate_kagylo_csapda,
    can_activate_onfelaldozo_esku,
    can_activate_meglepetesszeru_ellenakcio,
    can_activate_vegzetes_lepes,
    can_activate_vakito_visszavagas,
)


ON_PLAY_HANDLERS = {
    "goblin taktika": handle_goblin_taktika,
    "fenykard csapas": handle_fenykard_csapas,
    "felderito bagoly": handle_felderito_bagoly,
    "legaramlat-magus": handle_legaramlat_magus,
    "sikatori zsebtolvaj": handle_sikatori_zsebtolvaj,
    "aeterna aldasa": handle_aeterna_aldasa,
    "apaly es dagaly": handle_apaly_es_dagaly,
    "koborlo lelek": handle_koborlo_lelek,
    "sirba teres": handle_sirba_teres,
    "hirtelen dagaly": handle_hirtelen_dagaly,
    "kodbe vesz": handle_kodbe_vesz,
    "tukrozodo remeny": handle_tukrozodo_remeny,
    "a feny utja": handle_a_feny_utja,
    "a feny neve": handle_a_feny_neve,
    "keresztes hadjarat": handle_keresztes_hadjarat,
    "gyorsitott menet": handle_gyorsitott_menet,
    "vamszedo pont": handle_vamszedo_pont,
    "martirok vedelme": handle_martirok_vedelme,
    "megtorlo feny": handle_megtorlo_feny,
    "a vilagok keresztezodese": handle_a_vilagok_keresztezodese,
    "csapdaallito": handle_csapdaallito,
    "kove valas": handle_kove_valas,
    "megtisztulas": handle_megtisztulas,
    "isteni erintes": handle_isteni_erintes,
    "a hulladektelep": handle_a_hulladektelep,
    "alvilagi kapcsolatok": handle_alvilagi_kapcsolatok,
    "az orok elet temploma": handle_az_orok_elet_temploma,
    "informacio-vasarlas": handle_informacio_vasarlas,
    "rendszerfrissites": handle_rendszerfrissites,
    "a gyenge elhullik": handle_a_gyenge_elhullik,
    "a valtozo sziget": handle_a_valtozo_sziget,
    "varatlan apaly": handle_varatlan_apaly,
    "nagy aramlas": handle_nagy_aramlas,
    "vizeses golem": handle_vizeses_golem,
    "kraken-idomar": handle_kraken_idomar,
    "zatony-felderito": handle_zatony_felderito,
    "a zatony eneke": handle_a_zatony_eneke,
    "melytengeri nyomas": handle_melytengeri_nyomas,
    "vakito fust": handle_vakito_fust,
    "vakito seregek": handle_vakito_seregek,
    "surgeto hullam": handle_surgeto_hullam,
    "szentjanosbogar-raj": handle_szentjanosbogar_raj,
    "vakito szikra": handle_vakito_szikra,
    "vadon szeme ijasz": handle_vadon_szeme_ijasz,
    "langnyelv adeptus": handle_langnyelv_adeptus,
    "magma-elemental": handle_magma_elemental,
    "magma elemental": handle_magma_elemental,
    "vakito ragyogas": handle_vakito_ragyogas,
    "buborek-pajzs": handle_buborek_pajzs,
    "buborek pajzs": handle_buborek_pajzs,
    "langok vedelme": handle_langok_vedelme,
    "folyekony pancel": handle_folyekony_pancel,
    "vedelmezo burok": handle_vedelmezo_burok,
    "uresseg-kutato": handle_uresseg_kutato,
    "lelekmentes": handle_lelekmentes,
    "tuzeso": handle_tuzeso,
    "goznyomasos kiloves": handle_goznyomasos_kiloves,
    "visszahivas az uressegbol": handle_visszahivas_az_uressegbol,
    "gyar-felugyelo": handle_gyar_felugyelo,
    "a tomegtermeles gyara": handle_a_tomegtermeles_gyara,
    "egi emeles": handle_egi_emeles,
    "langnyelvek tanca": handle_langnyelvek_tanca,
    "pusztito roham": handle_pusztito_roham,
    "ork tabor": handle_ork_tabor,
    "varatlan gyulladas": handle_varatlan_gyulladas,
    "hamuba fojtas": handle_hamuba_fojtas,
    "tengeri delibab": handle_tengeri_delibab,
    "kitero manover": handle_kitero_manover,
    "megvesztegetes": handle_megvesztegetes,
    "szegecsvihar": handle_szegecsvihar,
    "a termeszet szava": handle_a_termeszet_szava,
    "ujjaszuletes fenye": handle_ujjaszuletes_fenye,
    "viharos menekules": handle_viharos_menekules,
    "univerzalis csere": handle_univerzalis_csere,
    "kod-alak": handle_kod_alak,
    "lopakodo felcser-dron": handle_lopakodo_felcser_dron,
    "sivatagi kem": handle_sivatagi_kem,
    "viz alatti borton": handle_viz_alatti_borton,
    "eletado fopap": handle_eletado_fopap,
    "szent lang inkvizitor": handle_szent_lang_inkvizitor,
}

TRAP_HANDLERS = {
    "varatlan erosites": handle_varatlan_erosites,
    "hamis arany": handle_hamis_arany,
    "lathatatlan fal": handle_lathatatlan_fal,
    "onfelaldozo esku": handle_onfelaldozo_esku,
    "meglepetesszeru ellenakcio": handle_meglepetesszeru_ellenakcio,
    "tornado csapda": handle_tornado_csapda,
    "benito fagy": handle_benito_fagy,
    "vakito visszavagas": handle_vakito_visszavagas,
    "vegzetes lepes": handle_vegzetes_lepes,
    "csuszos talaj": handle_csuszos_talaj,
    "orveny-nyeles": handle_orveny_nyeles,
    "atkozott orveny": handle_atkozott_orveny,
}

SUMMON_TRAP_HANDLERS = {
    "csapda a fustben": handle_csapda_a_fustben,
    "hamis igeret": handle_hamis_igeret,
    "kereskedelmi embargo": handle_kereskedelmi_embargo,
    "a melyseg szeme": handle_a_melyseg_szeme,
    "viharos ellencsapas": handle_viharos_ellencsapas,
    "kagylocsapda": handle_kagylo_csapda,
    "kagylo csapda": handle_kagylo_csapda,
}

TRAP_PREVIEW_HANDLERS = {
    "varatlan erosites": can_activate_varatlan_erosites,
    "hamis arany": can_activate_hamis_arany,
    "hamis igeret": can_activate_hamis_igeret,
    "kereskedelmi embargo": can_activate_kereskedelmi_embargo,
    "angyali beavatkozas": can_activate_angyali_beavatkozas,
    "hamis bizonyitek": can_activate_hamis_bizonyitek,
    "hamis halal": can_activate_hamis_halal,
    "eletmento burok": lambda *_, **__: False,
    "fa-oleles": lambda *_, **__: False,
    "fa oleles": lambda *_, **__: False,
    "a melyseg szeme": lambda *_, **__: False,
    "csaloka hullam": lambda *_, **__: False,
    "zart sorkepzes": lambda *_, **__: False,
    "lathatatlan fal": lambda card, target_kind=None, **_: target_kind == "seal",
    "megtorlo feny": lambda *_, **__: False,
    "martirok vedelme": lambda *_, **__: False,
    "onfelaldozo esku": can_activate_onfelaldozo_esku,
    "meglepetesszeru ellenakcio": can_activate_meglepetesszeru_ellenakcio,
    "vegzetes lepes": can_activate_vegzetes_lepes,
    "tornado csapda": lambda card, tamado_egyseg=None, **_: tamado_egyseg is not None,
    "benito fagy": can_activate_benito_fagy,
    "vakito visszavagas": can_activate_vakito_visszavagas,
    "csuszos talaj": can_activate_csuszos_talaj,
    "orveny-nyeles": can_activate_orveny_nyeles,
    "atkozott orveny": can_activate_atkozott_orveny,
    "tulhevult kazan": lambda *_, **__: False,
    "viharos ellencsapas": lambda *_, **__: False,
    "kagylocsapda": can_activate_kagylo_csapda,
    "kagylo csapda": can_activate_kagylo_csapda,
}

BURST_HANDLERS = {
    "a feny utja": handle_a_feny_utja,
    "fenykard csapas": handle_fenykard_csapas,
    "fustbomba": handle_fustbomba,
    "vakito szikra": handle_vakito_szikra,
    "vakito ragyogas": handle_vakito_ragyogas,
    "langok vedelme": handle_langok_vedelme,
    "lelekmentes": handle_lelekmentes,
    "hirtelen dagaly": handle_hirtelen_dagaly,
    "vakito fust": handle_vakito_fust,
    "surgeto hullam": handle_surgeto_hullam,
    "vedelmezo burok": handle_vedelmezo_burok,
    "varatlan gyulladas": handle_varatlan_gyulladas,
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
    elif category == "burst":
        handler = BURST_HANDLERS.get(key)
    else:
        handler = None

    if handler is None:
        return {"status": "unhandled", "category": category, "resolved": False}

    result = handler(card, **context) or {}
    result.setdefault("status", "handled")
    result.setdefault("category", category)
    result.setdefault("resolved", True)
    return result


def has_card_handler(card, category="on_play"):
    key = _handler_key(card)
    if category == "on_play":
        return key in ON_PLAY_HANDLERS
    if category == "trap":
        return key in TRAP_HANDLERS
    if category == "summon_trap":
        return key in SUMMON_TRAP_HANDLERS
    if category == "burst":
        return key in BURST_HANDLERS
    return False


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
trigger_engine.register("on_damage_taken", on_damage_taken_priority)
trigger_engine.register("on_turn_end", on_turn_end_priority)
