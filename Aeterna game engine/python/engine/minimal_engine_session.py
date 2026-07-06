"""Minimal AETERNA engine session boundary for the current smoke slice.

This is not the full rules engine and not a final Python-runtime decision. It
wraps the existing minimal engine facade so callers have one small session
object for match state, legal actions, action requests, diagnostics, event log,
and debug snapshots.

Player-visible snapshots are intentionally not implemented here. The current
snapshot helper is debug-only and must not be treated as a player-facing view.
"""

from __future__ import annotations

try:
    import minimal_engine
except ModuleNotFoundError:
    from . import minimal_engine


class MinimalEngineSession:
    """Small session wrapper over the existing minimal end_turn smoke facade."""

    def __init__(self, runtime_package):
        self.runtime_package = runtime_package
        self.state = None
        self.deck_id_a = None
        self.deck_id_b = None

    def create_match(self, deck_id_a=None, deck_id_b=None, match_id=None):
        deck_id_a, deck_id_b = self._resolve_decks(deck_id_a, deck_id_b)
        self.deck_id_a = deck_id_a
        self.deck_id_b = deck_id_b
        self.state = minimal_engine.create_match(
            self.runtime_package,
            deck_id_a,
            deck_id_b,
            match_id=match_id or "ENGINE-SESSION-SMOKE-001",
        )
        return self.state

    def get_debug_snapshot(self):
        state = self._require_state()
        diagnostics = self.get_diagnostics()
        legal_actions = self.list_legal_actions()
        return minimal_engine.create_debug_snapshot(state, legal_actions, diagnostics)

    def get_player_snapshot(self, player_id):
        state = self._require_state()
        diagnostics = self.get_diagnostics()
        legal_actions = self.list_legal_actions(player_id)
        return minimal_engine.create_player_visible_snapshot(state, player_id, legal_actions, diagnostics)

    def list_legal_actions(self, player_id=None):
        return minimal_engine.get_legal_actions(self._require_state(), player_id)

    def submit_action_request(self, request):
        state = self._require_state()
        legal_actions = self.list_legal_actions()
        response = minimal_engine.resolve_request(state, request, legal_actions)
        diagnostics = self.get_diagnostics()
        action = response.get("action") or {}
        return {
            "request_id": response.get("request_id"),
            "accepted": bool(response.get("accepted")),
            "reason": response.get("reason"),
            "action_type": action.get("action_type") or (request or {}).get("action_type"),
            "events": list(response.get("events") or []),
            "event_count": int(response.get("event_count") or 0),
            "state_version_before": response.get("state_version_before"),
            "state_version_after": response.get("state_version_after"),
            "new_event_sequences": list(response.get("new_event_sequences") or []),
            "diagnostics": diagnostics,
            "invariants_ok": len(diagnostics) == 0,
        }

    def step(self, request):
        return self.submit_action_request(request)

    def get_event_log(self, since=None):
        events = minimal_engine.event_log(self._require_state())
        if since is None:
            return events
        return events[int(since) :]

    def get_diagnostics(self):
        return minimal_engine.validate_invariants(self._require_state(), self.runtime_package)

    def export_smoke_report(self):
        state = self._require_state()
        snapshot = self.get_debug_snapshot()
        diagnostics = self.get_diagnostics()
        events = self.get_event_log()
        return {
            "schema_version": "minimal-engine-session-report-v0",
            "report_type": "minimal_engine_session",
            "runtime_decision_note": (
                "MinimalEngineSession is a reference smoke/backend candidate, "
                "not a final Python-runtime decision."
            ),
            "match": {
                "match_id": state.match_id,
                "state_version": state.state_version,
                "turn": state.turn_number,
                "phase": state.phase,
                "active_player_id": state.active_player_id,
            },
            "decks": {
                "deck_id_a": self.deck_id_a,
                "deck_id_b": self.deck_id_b,
            },
            "snapshot": snapshot,
            "player_snapshot_summary": self._player_snapshot_summary(self.get_player_snapshot(state.active_player_id)),
            "events": {
                "event_count": len(events),
                "last_event_sequence": events[-1].get("event_sequence") if events else None,
                "event_log": events,
            },
            "diagnostics": {
                "count": len(diagnostics),
                "blocking_errors": len(diagnostics),
                "errors": diagnostics,
            },
        }

    def build_action_request(self, action, player_id=None):
        state = self._require_state()
        return minimal_engine.build_action_request(state, action, player_id=player_id)

    def validate_action_request(self, request):
        return minimal_engine.validate_request(self._require_state(), request, self.list_legal_actions())

    def _require_state(self):
        if self.state is None:
            raise MinimalEngineSessionError("create_match() must be called before using the session.")
        return self.state

    def _resolve_decks(self, deck_id_a, deck_id_b):
        if deck_id_a and deck_id_b:
            return deck_id_a, deck_id_b
        preferred = ["DECK-IGN-HAM-TEST-001", "DECK-IGN-LAN-TEST-001"]
        available = sorted(self.runtime_package.decks_by_id)
        selected = [deck_id for deck_id in preferred if deck_id in self.runtime_package.decks_by_id]
        for deck_id in available:
            if deck_id not in selected:
                selected.append(deck_id)
            if len(selected) >= 2:
                break
        if len(selected) < 2:
            raise MinimalEngineSessionError("The runtime package must contain at least two decks.")
        return deck_id_a or selected[0], deck_id_b or selected[1]

    def _player_snapshot_summary(self, snapshot):
        return {
            "snapshot_type": snapshot["snapshot_type"],
            "visibility_mode": snapshot["visibility_mode"],
            "player_id": snapshot["player_id"],
            "hidden_information_model": snapshot["metadata"]["hidden_information_model"],
        }


class MinimalEngineSessionError(Exception):
    """Raised when the minimal session boundary cannot answer a request."""
