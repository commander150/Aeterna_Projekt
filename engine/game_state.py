from dataclasses import dataclass


@dataclass
class MatchState:
    p1: object
    p2: object
    kor: int = 1

    @property
    def players(self):
        return (self.p1, self.p2)
