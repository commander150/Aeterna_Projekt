from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from engine.config import EngineConfig


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
