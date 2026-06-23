from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional


DEFAULT_EXPANSION_MODULES = {
    "aeternal_abilities": False,
    "new_realms": False,
    "advanced_burst": False,
    "advanced_keywords": False,
    "resonance_fusion": False,
    "link_attack": False,
    "avatars_extra_deck": False,
}


DEFAULT_EXPANSION_FLAGS = {
    "aeternal_basic": False,
    "aeternal_tactical": False,
    "aeternal_ultimate": False,
    "depletion_tiers": False,
    "swarm_keyword": False,
    "realm_fulgur": False,
    "realm_crystalia": False,
    "realm_glacies": False,
    "realm_natura": False,
    "realm_chalybs": False,
    "realm_exul": False,
    "burst_categorized": False,
    "burst_destroying": False,
    "burst_tactical": False,
    "keyword_stealth": False,
    "keyword_sanctuary": False,
    "keyword_assassinate": False,
    "keyword_overclock": False,
    "keyword_soulguard": False,
    "training": False,
    "overcharge": False,
    "scry": False,
    "decoy": False,
    "mutation_advanced": False,
    "root_source_trigger": False,
    "pure_resonance": False,
    "elemental_fusion": False,
    "harmonized_field": False,
    "link_attack_keyword": False,
    "avatars": False,
    "extra_deck": False,
    "evolution": False,
    "aura_burn_avatar": False,
}


RUN_MODES = {
    "core_only",
    "core_plus_selected_expansions",
    "full_expansion_all_on",
    "debug_custom_flags",
}


@dataclass
class EngineConfig:
    run_mode: str = "core_only"
    expansion_modules: Dict[str, bool] = field(default_factory=lambda: dict(DEFAULT_EXPANSION_MODULES))
    expansion_flags: Dict[str, bool] = field(default_factory=lambda: dict(DEFAULT_EXPANSION_FLAGS))

    def __post_init__(self):
        if self.run_mode not in RUN_MODES:
            raise ValueError(f"Ismeretlen futasi mod: {self.run_mode}")

        merged_modules = dict(DEFAULT_EXPANSION_MODULES)
        merged_modules.update(self.expansion_modules or {})
        merged_flags = dict(DEFAULT_EXPANSION_FLAGS)
        merged_flags.update(self.expansion_flags or {})

        if self.run_mode == "full_expansion_all_on":
            merged_modules = {kulcs: True for kulcs in merged_modules}
            merged_flags = {kulcs: True for kulcs in merged_flags}
        elif self.run_mode == "core_only":
            merged_modules = {kulcs: False for kulcs in merged_modules}
            merged_flags = {kulcs: False for kulcs in merged_flags}

        self.expansion_modules = merged_modules
        self.expansion_flags = merged_flags

    def is_module_enabled(self, module_name: str) -> bool:
        return bool(self.expansion_modules.get(module_name, False))

    def is_flag_enabled(self, flag_name: str) -> bool:
        return bool(self.expansion_flags.get(flag_name, False))

    def active_modules(self) -> Iterable[str]:
        return [kulcs for kulcs, aktiv in self.expansion_modules.items() if aktiv]

    def active_flags(self) -> Iterable[str]:
        return [kulcs for kulcs, aktiv in self.expansion_flags.items() if aktiv]

    def describe(self) -> str:
        aktiv_modulok = ", ".join(self.active_modules()) or "none"
        aktiv_flagek = ", ".join(self.active_flags()) or "none"
        return (
            f"run_mode={self.run_mode}, "
            f"modules=[{aktiv_modulok}], "
            f"flags=[{aktiv_flagek}]"
        )


_AKTIV_ENGINE_CONFIG = EngineConfig()


def set_active_engine_config(config: Optional[EngineConfig]) -> EngineConfig:
    global _AKTIV_ENGINE_CONFIG
    _AKTIV_ENGINE_CONFIG = config or EngineConfig()
    return _AKTIV_ENGINE_CONFIG


def get_active_engine_config() -> EngineConfig:
    return _AKTIV_ENGINE_CONFIG
