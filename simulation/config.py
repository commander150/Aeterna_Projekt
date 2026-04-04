from dataclasses import dataclass, field
from typing import Any, Dict, Optional


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

    def describe(self) -> str:
        return (
            f"games={self.games}, "
            f"seed={self.random_seed if self.random_seed is not None else 'random'}, "
            f"p1_realm={self.player1_realm or 'random'}, "
            f"p2_realm={self.player2_realm or 'random'}, "
            f"random_fallback={'on' if self.random_realm_fallback else 'off'}, "
            f"scenario={self.scenario or 'none'}"
        )
