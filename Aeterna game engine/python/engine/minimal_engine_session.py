"""Minimal AETERNA engine session boundary for the current smoke slice.

This is not the full rules engine and not a final Python-runtime decision. It
wraps the existing minimal engine facade so callers have one small session
object for match state, legal actions, action requests, diagnostics, event log,
and debug snapshots.

Player-visible snapshots are intentionally not implemented here. The current
snapshot helper is debug-only and must not be treated as a player-facing view.
"""

from __future__ import annotations

from copy import deepcopy

try:
    import minimal_engine
except ModuleNotFoundError:
    from . import minimal_engine


class MinimalEngineSession:
    """Small session wrapper over the existing minimal end_turn smoke facade.

    step() is only a convenience wrapper over submit_action_request(); it is not
    a separate rules path.
    """

    def __init__(self, runtime_package):
        self.runtime_package = runtime_package
        self.state = None
        self.deck_id_a = None
        self.deck_id_b = None
        self._action_response_history = []

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
        self._action_response_history = []
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

    def get_action_space(self, player_id=None):
        state = self._require_state()
        legal_actions = self.list_legal_actions(player_id)
        actions = [self._build_legal_action_contract(action) for action in legal_actions]
        return {
            "schema_version": "minimal-legal-action-space-v0",
            "contract_type": "legal_action_space",
            "match_id": state.match_id,
            "player_id": player_id or state.active_player_id,
            "state_version": state.state_version,
            "turn": state.turn_number,
            "phase": state.phase,
            "active_player_id": state.active_player_id,
            "priority_player_id": state.active_player_id,
            "actions": actions,
            "enabled_action_count": sum(1 for action in actions if action["enabled"] is True),
            "disabled_action_count": sum(1 for action in actions if action["enabled"] is not True),
            "metadata": {
                "source": "python.engine.minimal_engine_session",
                "rules_scope": "minimal_end_turn_smoke",
                "runtime_decision": "reference_smoke_backend_candidate",
            },
        }

    def submit_action_request(self, request):
        state = self._require_state()
        legal_actions = self.list_legal_actions()
        response = minimal_engine.resolve_request(state, request, legal_actions)
        contract = self._build_action_response_contract(request, response)
        self._action_response_history.append(deepcopy(contract))
        return deepcopy(contract)

    def step(self, request):
        return self.submit_action_request(request)

    def get_last_action_response(self):
        if not self._action_response_history:
            return None
        return deepcopy(self._action_response_history[-1])

    def get_action_response_history(self):
        return deepcopy(self._action_response_history)

    def get_transition_summary(self):
        state = self._require_state()
        events = self.get_event_log()
        responses = self._action_response_history
        accepted_count = sum(1 for response in responses if response.get("accepted") is True)
        rejected_count = sum(1 for response in responses if response.get("accepted") is not True)
        last_response = responses[-1] if responses else None
        return {
            "schema_version": "minimal-transition-summary-v0",
            "contract_type": "transition_summary",
            "match_id": state.match_id,
            "state_version": state.state_version,
            "turn": state.turn_number,
            "phase": state.phase,
            "active_player_id": state.active_player_id,
            "priority_player_id": state.active_player_id,
            "event_count": len(events),
            "last_event_sequence": events[-1].get("event_sequence") if events else None,
            "response_count": len(responses),
            "accepted_response_count": accepted_count,
            "rejected_response_count": rejected_count,
            "last_response_type": last_response.get("response_type") if last_response else None,
            "last_response_accepted": last_response.get("accepted") if last_response else None,
            "last_response_success": last_response.get("success") if last_response else None,
            "last_response_reason": last_response.get("reason") if last_response else None,
            "metadata": {
                "source": "python.engine.minimal_engine_session",
                "rules_scope": "minimal_end_turn_smoke",
                "runtime_decision": "reference_smoke_backend_candidate",
            },
        }

    def export_debug_session_state(self):
        state = self._require_state()
        diagnostics = self.get_diagnostics()
        debug_snapshot = self.get_debug_snapshot()
        action_space = self.get_action_space()
        transition_summary = self.get_transition_summary()
        return deepcopy(
            {
                "schema_version": "minimal-debug-session-state-v0",
                "contract_type": "debug_session_state",
                "match_id": state.match_id,
                "debug_snapshot": debug_snapshot,
                "action_space": action_space,
                "transition_summary": transition_summary,
                "last_action_response": self.get_last_action_response(),
                "diagnostics_summary": {
                    "count": len(diagnostics),
                    "blocking_errors": len(diagnostics),
                    "warnings": 0,
                },
                "metadata": {
                    "source": "python.engine.minimal_engine_session",
                    "rules_scope": "minimal_end_turn_smoke",
                    "runtime_decision": "not_final",
                    "replay_support": "not_implemented",
                    "replay_future_candidate": True,
                },
            }
        )

    def _build_action_response_contract(self, request, response):
        state = self._require_state()
        diagnostics = self.get_diagnostics()
        normalized_request = dict(request or {})
        action = response.get("action") or {}
        events = list(response.get("events") or [])
        action_type = action.get("action_type") or normalized_request.get("action_type")
        new_event_count = int(response.get("event_count") or 0)
        accepted = bool(response.get("accepted"))
        state_version_before = response.get("state_version_before")
        if state_version_before is None:
            state_version_before = state.state_version
        state_version_after = response.get("state_version_after")
        if state_version_after is None:
            state_version_after = state.state_version
        return {
            "schema_version": "minimal-action-response-v0",
            "contract_type": "action_response",
            "response_type": "minimal_action_response",
            "match_id": state.match_id,
            "request_id": response.get("request_id"),
            "player_id": normalized_request.get("player_id"),
            "action_id": normalized_request.get("action_id"),
            "action_type": action_type,
            "accepted": accepted,
            "success": accepted and len(diagnostics) == 0,
            "reason": response.get("reason"),
            "state_version_before": state_version_before,
            "state_version_after": state_version_after,
            "new_event_count": new_event_count,
            "event_count": new_event_count,
            "new_event_sequences": list(response.get("new_event_sequences") or []),
            "events": events,
            "diagnostics": diagnostics,
            "diagnostics_summary": {
                "count": len(diagnostics),
                "blocking_errors": len(diagnostics),
                "warnings": 0,
            },
            "invariants_ok": len(diagnostics) == 0,
            "metadata": {
                "source": "python.engine.minimal_engine_session",
                "rules_scope": "minimal_end_turn_smoke",
                "runtime_decision": "reference_smoke_backend_candidate",
            },
        }

    def _build_legal_action_contract(self, action):
        normalized = dict(action or {})
        enabled = normalized.get("enabled") is True
        player_id = normalized.get("player_id")
        action_type = normalized.get("action_type")
        return {
            "action_id": normalized.get("action_id"),
            "action_type": action_type,
            "player_id": player_id,
            "enabled": enabled,
            "disabled_reason": None if enabled else normalized.get("reason"),
            "request_template": {
                "action_type": action_type,
                "player_id": player_id,
                "payload": {},
                "required_fields": ["match_id", "player_id", "action_id", "action_type"],
            },
            "metadata": {
                "source": "rules_kernel.list_legal_actions",
                "rules_scope": "minimal_end_turn_smoke",
            },
        }

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
            "response_history_count": len(self._action_response_history),
            "transition_summary": self.get_transition_summary(),
            "debug_session_state_summary": self._debug_session_state_summary(self.export_debug_session_state()),
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

    def _debug_session_state_summary(self, debug_session_state):
        transition_summary = debug_session_state["transition_summary"]
        return {
            "contract_type": debug_session_state["contract_type"],
            "state_version": transition_summary["state_version"],
            "response_count": transition_summary["response_count"],
            "event_count": transition_summary["event_count"],
            "replay_support": debug_session_state["metadata"]["replay_support"],
        }


class MinimalEngineSessionError(Exception):
    """Raised when the minimal session boundary cannot answer a request."""
