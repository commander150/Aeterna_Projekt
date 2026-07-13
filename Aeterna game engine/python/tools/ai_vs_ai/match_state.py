"""Minimal match state for AI smoke rules-kernel work."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlayerState:
    player_id: str
    deck_id: str
    deck_card_instance_ids: list
    hand_card_instance_ids: list = field(default_factory=list)
    discard_card_instance_ids: list = field(default_factory=list)


@dataclass
class MatchState:
    match_id: str
    turn_number: int
    active_player_id: str
    players: list
    phase: str
    card_instances: dict = field(default_factory=dict)
    # 0 means the initial state before any accepted transition.
    state_version: int = 0
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

    def get_card_instance(self, card_instance_id):
        try:
            return self.card_instances[card_instance_id]
        except (KeyError, TypeError) as exc:
            raise MatchStateError("Unknown card_instance_id: %s" % card_instance_id) from exc

    def get_card_id(self, card_instance_id):
        return self.get_card_instance(card_instance_id).get("card_id")


class MatchStateError(Exception):
    """Raised when a match state cannot answer a basic query."""
