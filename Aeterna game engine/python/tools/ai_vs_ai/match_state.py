"""Minimal match state for AI smoke rules-kernel work."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlayerState:
    player_id: str
    deck_id: str
    deck_card_ids: list
    hand: list = field(default_factory=list)
    discard: list = field(default_factory=list)


@dataclass
class MatchState:
    match_id: str
    turn_number: int
    active_player_id: str
    players: list
    phase: str
    event_log: list = field(default_factory=list)

    def get_player(self, player_id):
        for player in self.players:
            if player.player_id == player_id:
                return player
        raise MatchStateError("Unknown player_id: %s" % player_id)

    def get_inactive_player_id(self):
        for player in self.players:
            if player.player_id != self.active_player_id:
                return player.player_id
        raise MatchStateError("No inactive player found.")


class MatchStateError(Exception):
    """Raised when a match state cannot answer a basic query."""
