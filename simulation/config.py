from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from engine.config import EngineConfig


CANONICAL_REALMS = (
    "Aether",
    "Aqua",
    "Ignis",
    "Lux",
    "Terra",
    "Umbra",
    "Ventus",
)

_REALM_LOOKUP = {realm.lower(): realm for realm in CANONICAL_REALMS}


def normalize_realm_name(value: Optional[str]) -> Optional[str]:
    if value in (None, "", "random", "veletlen", "none"):
        return None
    cleaned = str(value).strip()
    if cleaned == "":
        return None
    return _REALM_LOOKUP.get(cleaned.lower(), cleaned)


@dataclass
class SimulationConfig:
    games: int = 3
    random_seed: Optional[int] = None
    player1_realm: Optional[str] = None
    player2_realm: Optional[str] = None
    random_realm_fallback: bool = True

    # kesobbi boviteshez
    player1_deck: Optional[Any] = None
    player2_deck: Optional[Any] = None
    scenario: Optional[str] = None
    scripted_opening_hands: Dict[str, Any] = field(default_factory=dict)
    scripted_board_state: Optional[Dict[str, Any]] = None
    engine_run_mode: str = "core_only"
    expansion_modules: Dict[str, bool] = field(default_factory=dict)
    expansion_flags: Dict[str, bool] = field(default_factory=dict)
    log_base_dir: Optional[str] = None

    def __post_init__(self):
        self.player1_realm = normalize_realm_name(self.player1_realm)
        self.player2_realm = normalize_realm_name(self.player2_realm)

    def to_engine_config(self) -> EngineConfig:
        return EngineConfig(
            run_mode=self.engine_run_mode,
            expansion_modules=self.expansion_modules,
            expansion_flags=self.expansion_flags,
        )

    def describe(self) -> str:
        return (
            f"games={self.games}, "
            f"seed={self.random_seed if self.random_seed is not None else 'random'}, "
            f"p1_realm={self.player1_realm or 'random'}, "
            f"p2_realm={self.player2_realm or 'random'}, "
            f"random_fallback={'on' if self.random_realm_fallback else 'off'}, "
            f"scenario={self.scenario or 'none'}, "
            f"engine={self.to_engine_config().describe()}"
        )
