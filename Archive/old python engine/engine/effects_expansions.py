from __future__ import annotations

from typing import Optional, Tuple

from engine.config import get_active_engine_config
from engine.logging_utils import log_flag_skip
from utils.text import normalize_lookup_text


EXPANSION_RULES = [
    {
        "module": "aeternal_abilities",
        "flag": None,
        "patterns": ("aeternal", "basic:", "tactical:", "ultimate:"),
    },
    {
        "module": "new_realms",
        "flag": "swarm_keyword",
        "patterns": ("rajzas", "swarm"),
    },
    {
        "module": "new_realms",
        "flag": "realm_fulgur",
        "patterns": ("bind", "szamuzetes", "exile"),
    },
    {
        "module": "new_realms",
        "flag": "realm_crystalia",
        "patterns": ("mirror-step", "mirror step"),
    },
    {
        "module": "new_realms",
        "flag": "realm_glacies",
        "patterns": ("freeze", "zarolas"),
    },
    {
        "module": "new_realms",
        "flag": "realm_natura",
        "patterns": ("mutation", "mutacio"),
    },
    {
        "module": "new_realms",
        "flag": "realm_chalybs",
        "patterns": ("equip", "szerulek"),
    },
    {
        "module": "new_realms",
        "flag": "realm_exul",
        "patterns": ("oblivion", "mill"),
    },
    {
        "module": "advanced_burst",
        "flag": "burst_categorized",
        "patterns": ("healing burst", "awakening burst", "interrupt burst"),
    },
    {
        "module": "advanced_burst",
        "flag": "burst_destroying",
        "patterns": ("destroying burst",),
    },
    {
        "module": "advanced_burst",
        "flag": "burst_tactical",
        "patterns": ("tactical burst",),
    },
    {
        "module": "advanced_keywords",
        "flag": "keyword_stealth",
        "patterns": ("stealth",),
    },
    {
        "module": "advanced_keywords",
        "flag": "keyword_sanctuary",
        "patterns": ("sanctuary",),
    },
    {
        "module": "advanced_keywords",
        "flag": "keyword_assassinate",
        "patterns": ("assassinate",),
    },
    {
        "module": "advanced_keywords",
        "flag": "keyword_overclock",
        "patterns": ("overclock",),
    },
    {
        "module": "advanced_keywords",
        "flag": "keyword_soulguard",
        "patterns": ("soulguard",),
    },
    {
        "module": "advanced_keywords",
        "flag": "training",
        "patterns": ("training",),
    },
    {
        "module": "advanced_keywords",
        "flag": "overcharge",
        "patterns": ("overcharge",),
    },
    {
        "module": "advanced_keywords",
        "flag": "scry",
        "patterns": ("scry",),
    },
    {
        "module": "advanced_keywords",
        "flag": "decoy",
        "patterns": ("decoy",),
    },
    {
        "module": "advanced_keywords",
        "flag": "root_source_trigger",
        "patterns": ("root",),
    },
    {
        "module": "resonance_fusion",
        "flag": "pure_resonance",
        "patterns": ("pure resonance", "tiszta rezonancia"),
    },
    {
        "module": "resonance_fusion",
        "flag": "elemental_fusion",
        "patterns": ("elemental fusion", "elemi fuzio"),
    },
    {
        "module": "resonance_fusion",
        "flag": "harmonized_field",
        "patterns": ("harmonized field", "harmonizalt mezo"),
    },
    {
        "module": "link_attack",
        "flag": "link_attack_keyword",
        "patterns": ("link [", "link attack", "kapcsolt tamadas"),
    },
    {
        "module": "avatars_extra_deck",
        "flag": "avatars",
        "patterns": ("avatar",),
    },
    {
        "module": "avatars_extra_deck",
        "flag": "extra_deck",
        "patterns": ("extra deck", "extra pakli"),
    },
    {
        "module": "avatars_extra_deck",
        "flag": "evolution",
        "patterns": ("evolution", "evolucio"),
    },
    {
        "module": "avatars_extra_deck",
        "flag": "aura_burn_avatar",
        "patterns": ("aura burn", "aura egetes"),
    },
]


def classify_expansion_requirement(effect_text: str) -> Optional[Tuple[str, Optional[str]]]:
    text = normalize_lookup_text(effect_text)
    if not text or text == "-":
        return None

    for szabaly in EXPANSION_RULES:
        if any(minta in text for minta in szabaly["patterns"]):
            return szabaly["module"], szabaly["flag"]
    return None


def handle_expansion_gate(card_name: str, effect_text: str) -> bool:
    igeny = classify_expansion_requirement(effect_text)
    if igeny is None:
        return False

    module_name, flag_name = igeny
    config = get_active_engine_config()

    if not config.is_module_enabled(module_name):
        log_flag_skip(card_name, module_name)
        return True

    if flag_name and not config.is_flag_enabled(flag_name):
        log_flag_skip(card_name, flag_name)
        return True

    return False
