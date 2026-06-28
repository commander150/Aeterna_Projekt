"""Deterministic bot policy for AI smoke tests.

The policy does not generate actions and does not modify state. It only chooses
from legal actions already provided by the rules kernel.
"""

from __future__ import annotations


ACTION_PRIORITIES = {
    "play_card": 10,
    "activate": 20,
    "end_turn": 100,
}


class BotPolicyError(Exception):
    """Raised when the bot has no valid action to choose."""


class DeterministicBotPolicy:
    def choose_action(self, legal_actions, player_id):
        candidates = [
            action
            for action in list(legal_actions or [])
            if action.get("enabled") is True and action.get("player_id") == player_id
        ]
        if not candidates:
            raise BotPolicyError("No enabled legal action for player_id: %s" % player_id)
        return dict(sorted(candidates, key=_action_sort_key)[0])


def choose_action(legal_actions, player_id):
    return DeterministicBotPolicy().choose_action(legal_actions, player_id)


def _action_sort_key(action):
    return (
        ACTION_PRIORITIES.get(action.get("action_type"), 999),
        str(action.get("action_id") or ""),
    )
