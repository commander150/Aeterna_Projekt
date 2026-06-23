from dataclasses import dataclass


@dataclass
class MatchState:
    p1: object
    p2: object
    kor: int = 1
    active_player: object | None = None
    phase: str = "setup"
    match_finished: bool = False
    winner: object | None = None
    victory_reason: str | None = None

    @property
    def players(self):
        return (self.p1, self.p2)
