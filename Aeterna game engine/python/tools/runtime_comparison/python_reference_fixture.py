"""Deterministic in-memory Python runner for the canonical comparison fixture."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from engine.minimal_engine_session import MinimalEngineSession
from tools.ai_vs_ai.runtime_package_reader import RuntimePackageReadError, load_runtime_package

from .canonical_json import canonical_json_bytes, sha256_bytes


FIXTURE_SCHEMA_VERSION = "aeterna-runtime-comparison-fixture-v1"
FIXTURE_ID = "minimal_draw_end_turn_v1"
RESULT_SCHEMA_VERSION = "aeterna-python-reference-fixture-run-v1"

REQUEST_IDS = {
    "draw_player_1": "fixture_req_001_draw_player_1",
    "stale_end_turn_player_1": "fixture_req_002_stale_end_turn_player_1",
    "end_turn_player_1": "fixture_req_003_end_turn_player_1",
    "draw_player_2": "fixture_req_004_draw_player_2",
}

LEGAL_ACTION_ORDER_RANKS = {
    "end_turn": 100,
    "draw_card": 200,
}

_REQUEST_FIELDS = {
    "request_id",
    "match_id",
    "player_id",
    "action_id",
    "action_type",
    "expected_state_version",
    "payload",
}

_IMPLEMENTATION_METADATA_KEYS = {
    "source",
    "source_module",
    "authority",
    "runtime_decision",
    "module",
    "component",
    "class",
    "class_name",
    "function",
    "function_name",
    "build",
    "build_id",
    "build_path",
    "path",
}

_FORBIDDEN_PLAYER_SNAPSHOT_KEYS = {
    "card_instances",
    "event_log",
    "debug_snapshot",
    "domain_topologies",
    "domain_occupancies",
}


class RuntimeComparisonFixtureError(Exception):
    """Stable fixture-runner failure without implementation-specific details."""

    def __init__(self, code, step_id, message, details=None):
        self.code = str(code)
        self.step_id = str(step_id)
        self.message = str(message)
        self.details = deepcopy(details or {})
        canonical_json_bytes(self.to_dict())
        super().__init__("%s [%s]: %s" % (self.code, self.step_id, self.message))

    def to_dict(self):
        return {
            "code": self.code,
            "step_id": self.step_id,
            "message": self.message,
            "details": deepcopy(self.details),
        }


def run_python_reference_fixture(fixture_path):
    """Run the fixed minimal comparison plan and return JSON-compatible data."""

    runner = _PythonReferenceFixtureRunner(fixture_path)
    try:
        return runner.run()
    except RuntimeComparisonFixtureError:
        raise
    except Exception:
        raise RuntimeComparisonFixtureError(
            "FIXTURE_RUN_FAILED",
            runner.step_id,
            "Fixture execution failed.",
        ) from None


class _PythonReferenceFixtureRunner:
    def __init__(self, fixture_path):
        self.fixture_path = Path(fixture_path)
        self.step_id = "load_fixture"

    def run(self):
        fixture = self._load_fixture()
        runtime_package = self._load_runtime_package(fixture)
        session = MinimalEngineSession(runtime_package)

        self.step_id = "step_0_initial_validation"
        session.create_match(
            deck_id_a=fixture["deck_ids"][0],
            deck_id_b=fixture["deck_ids"][1],
            match_id=fixture["match_id"],
            player_ids=tuple(fixture["player_ids"]),
            starting_hand_size=fixture["starting_hand_size"],
        )
        initial_state = session.export_canonical_match_state()
        self._assert_initial_state(initial_state, session.get_diagnostics(), fixture)

        legal_action_checkpoints = []
        initial_checkpoint, initial_action_space = self._record_action_checkpoint(
            session,
            "initial_v0",
            "player_1",
        )
        legal_action_checkpoints.append(initial_checkpoint)

        requests = []
        responses = []

        self.step_id = "step_1_draw_player_1"
        draw_player_1 = self._select_action(
            initial_action_space,
            "draw_card",
            "player_1",
        )
        draw_player_1_request = session.build_action_request(
            draw_player_1,
            player_id="player_1",
            request_id=REQUEST_IDS["draw_player_1"],
            expected_state_version=0,
            payload={},
        )
        draw_player_1_response = self._submit(
            session,
            draw_player_1_request,
            requests,
            responses,
        )
        self._assert_accepted_response(draw_player_1_response, 0, 1, "draw_card", 1)
        state_v1 = session.export_canonical_match_state()
        self._assert_player_zone_counts(state_v1, "player_1", hand_count=2, deck_count=1)
        self._assert_event_sequence(state_v1, ["zone_move"], [1])
        checkpoint_v1, action_space_v1 = self._record_action_checkpoint(
            session,
            "after_player_1_draw_v1",
            "player_1",
        )
        legal_action_checkpoints.append(checkpoint_v1)

        self.step_id = "step_2_stale_end_turn_player_1"
        stale_end_turn = self._select_action(
            action_space_v1,
            "end_turn",
            "player_1",
        )
        stale_request = session.build_action_request(
            stale_end_turn,
            player_id="player_1",
            request_id=REQUEST_IDS["stale_end_turn_player_1"],
            expected_state_version=0,
            payload={},
        )
        stale_request_before = deepcopy(stale_request)
        stale_state_before = session.export_canonical_match_state()
        stale_bytes_before = canonical_json_bytes(stale_state_before)
        stale_hash_before = sha256_bytes(stale_bytes_before)
        stale_response = self._submit(session, stale_request, requests, responses)
        stale_state_after = session.export_canonical_match_state()
        stale_bytes_after = canonical_json_bytes(stale_state_after)
        stale_hash_after = sha256_bytes(stale_bytes_after)
        self._assert_stale_response(stale_response)
        self._assert(
            stale_request == stale_request_before,
            "The stale request input was mutated.",
        )
        self._assert(
            stale_state_before == stale_state_after,
            "The stale rejection changed canonical MatchState.",
        )
        self._assert(
            stale_bytes_before == stale_bytes_after and stale_hash_before == stale_hash_after,
            "The stale rejection changed canonical state bytes or hash.",
        )
        stale_immutability = self._build_immutability_result(
            stale_state_before,
            stale_state_after,
            stale_hash_before,
            stale_hash_after,
            stale_request == stale_request_before,
        )

        self.step_id = "step_3_end_turn_player_1"
        current_end_turn = self._select_action(
            session.get_action_space("player_1"),
            "end_turn",
            "player_1",
        )
        end_turn_request = session.build_action_request(
            current_end_turn,
            player_id="player_1",
            request_id=REQUEST_IDS["end_turn_player_1"],
            expected_state_version=1,
            payload={},
        )
        end_turn_response = self._submit(session, end_turn_request, requests, responses)
        self._assert_accepted_response(end_turn_response, 1, 2, "end_turn", 2)
        state_v2 = session.export_canonical_match_state()
        self._assert(
            state_v2["active_player_id"] == "player_2"
            and state_v2["priority_player_id"] == "player_2",
            "The valid end_turn did not transfer active and priority player.",
        )
        self._assert_event_sequence(
            state_v2,
            ["zone_move", "turn_transition"],
            [1, 2],
        )
        checkpoint_v2, action_space_v2 = self._record_action_checkpoint(
            session,
            "after_player_1_end_turn_v2",
            "player_2",
        )
        legal_action_checkpoints.append(checkpoint_v2)

        self.step_id = "step_4_draw_player_2"
        draw_player_2 = self._select_action(
            action_space_v2,
            "draw_card",
            "player_2",
        )
        draw_player_2_request = session.build_action_request(
            draw_player_2,
            player_id="player_2",
            request_id=REQUEST_IDS["draw_player_2"],
            expected_state_version=2,
            payload={},
        )
        draw_player_2_response = self._submit(
            session,
            draw_player_2_request,
            requests,
            responses,
        )
        self._assert_accepted_response(draw_player_2_response, 2, 3, "draw_card", 3)
        state_v3 = session.export_canonical_match_state()
        self._assert_player_zone_counts(state_v3, "player_2", hand_count=2, deck_count=1)
        self._assert_event_sequence(
            state_v3,
            ["zone_move", "turn_transition", "zone_move"],
            [1, 2, 3],
        )
        checkpoint_v3, _action_space_v3 = self._record_action_checkpoint(
            session,
            "after_player_2_draw_v3",
            "player_2",
        )
        legal_action_checkpoints.append(checkpoint_v3)

        self.step_id = "step_5_player_1_snapshot"
        snapshot_player_1, player_1_visibility = self._capture_player_snapshot(
            session,
            "player_1",
        )

        self.step_id = "step_6_player_2_snapshot"
        snapshot_player_2, player_2_visibility = self._capture_player_snapshot(
            session,
            "player_2",
        )

        self.step_id = "step_7_final_validation"
        final_diagnostics = deepcopy(session.get_diagnostics())
        final_state = session.export_canonical_match_state()
        self._assert(not final_diagnostics, "Final state invariants are not valid.")
        self._assert(final_state["state_version"] == 3, "Final state_version must be 3.")
        self._assert(
            final_state["active_player_id"] == "player_2"
            and final_state["priority_player_id"] == "player_2",
            "Final active or priority player is invalid.",
        )
        self._assert_event_sequence(
            final_state,
            ["zone_move", "turn_transition", "zone_move"],
            [1, 2, 3],
        )

        canonical_responses = [_strip_implementation_metadata(item) for item in responses]
        stale_diagnostics = deepcopy(canonical_responses[1]["diagnostics"])
        result = {
            "schema_version": RESULT_SCHEMA_VERSION,
            "result_type": "python_reference_fixture_run",
            "fixture_identity": {
                "schema_version": fixture["schema_version"],
                "fixture_id": fixture["fixture_id"],
                "step_plan_id": fixture["step_plan"]["step_plan_id"],
                "match_id": fixture["match_id"],
                "seed": fixture["seed"],
                "runtime_package_id": runtime_package.manifest.get("package_id"),
            },
            "initial_canonical_state": initial_state,
            "requests": deepcopy(requests),
            "responses": canonical_responses,
            "legal_action_checkpoints": legal_action_checkpoints,
            "events": deepcopy(final_state["event_log"]),
            "snapshot_player_1": snapshot_player_1,
            "snapshot_player_2": snapshot_player_2,
            "final_canonical_state": final_state,
            "diagnostics": stale_diagnostics + final_diagnostics,
            "stale_immutability": stale_immutability,
            "visibility_checks": {
                "player_1": player_1_visibility,
                "player_2": player_2_visibility,
                "all_passed": player_1_visibility["passed"] and player_2_visibility["passed"],
            },
            "run_summary": {
                "completed": True,
                "request_count": len(requests),
                "accepted_response_count": 3,
                "rejected_response_count": 1,
                "state_version_path": [0, 1, 1, 2, 3],
                "event_count": len(final_state["event_log"]),
                "event_sequences": [event["event_sequence"] for event in final_state["event_log"]],
                "event_types": [event["event_type"] for event in final_state["event_log"]],
                "legal_action_checkpoint_count": len(legal_action_checkpoints),
                "invariant_error_count": len(final_diagnostics),
                "stale_state_unchanged": stale_immutability["canonical_state_unchanged"],
                "hidden_information_checks_passed": (
                    player_1_visibility["passed"] and player_2_visibility["passed"]
                ),
            },
        }
        self._assert_result_hygiene(result)
        canonical_json_bytes(result)
        return deepcopy(result)

    def _load_fixture(self):
        if not self.fixture_path.is_file():
            raise RuntimeComparisonFixtureError(
                "FIXTURE_NOT_FOUND",
                self.step_id,
                "Fixture file was not found.",
            )
        try:
            fixture = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            raise RuntimeComparisonFixtureError(
                "FIXTURE_JSON_INVALID",
                self.step_id,
                "Fixture file is not valid UTF-8 JSON.",
            ) from None
        if not isinstance(fixture, dict):
            raise RuntimeComparisonFixtureError(
                "FIXTURE_SHAPE_INVALID",
                self.step_id,
                "Fixture root must be an object.",
            )
        if fixture.get("schema_version") != FIXTURE_SCHEMA_VERSION:
            raise RuntimeComparisonFixtureError(
                "FIXTURE_SCHEMA_INVALID",
                self.step_id,
                "Fixture schema_version is not supported.",
            )
        if fixture.get("fixture_id") != FIXTURE_ID:
            raise RuntimeComparisonFixtureError(
                "FIXTURE_ID_INVALID",
                self.step_id,
                "Fixture ID is not supported by this runner.",
            )
        self._validate_fixture_shape(fixture)
        return deepcopy(fixture)

    def _validate_fixture_shape(self, fixture):
        valid = (
            fixture.get("player_ids") == ["player_1", "player_2"]
            and isinstance(fixture.get("deck_ids"), list)
            and len(fixture["deck_ids"]) == 2
            and isinstance(fixture.get("match_id"), str)
            and fixture["match_id"] != ""
            and fixture.get("starting_hand_size") == 1
            and isinstance(fixture.get("seed"), int)
            and not isinstance(fixture.get("seed"), bool)
            and isinstance(fixture.get("step_plan"), dict)
            and fixture["step_plan"].get("step_plan_id") == FIXTURE_ID
        )
        runtime_ref = fixture.get("runtime_package_ref")
        valid = valid and isinstance(runtime_ref, str) and runtime_ref != ""
        if valid:
            ref_path = Path(runtime_ref)
            valid = not ref_path.is_absolute() and ".." not in ref_path.parts
        if not valid:
            raise RuntimeComparisonFixtureError(
                "FIXTURE_SHAPE_INVALID",
                self.step_id,
                "Fixture fields do not match the fixed minimal comparison contract.",
            )

    def _load_runtime_package(self, fixture):
        self.step_id = "load_runtime_package"
        package_path = self.fixture_path.parent / fixture["runtime_package_ref"]
        try:
            runtime_package = load_runtime_package(package_path)
        except RuntimePackageReadError:
            raise RuntimeComparisonFixtureError(
                "RUNTIME_PACKAGE_INVALID",
                self.step_id,
                "Fixture runtime package could not be loaded.",
            ) from None
        if runtime_package.validate_deck_card_refs():
            raise RuntimeComparisonFixtureError(
                "RUNTIME_PACKAGE_INVALID",
                self.step_id,
                "Fixture runtime package contains invalid deck references.",
            )
        return runtime_package

    def _assert_initial_state(self, state, diagnostics, fixture):
        self._assert(not diagnostics, "Initial state invariants are not valid.")
        self._assert(state["match_id"] == fixture["match_id"], "Initial match_id is invalid.")
        self._assert(state["state_version"] == 0, "Initial state_version must be 0.")
        self._assert(state["event_log"] == [], "Initial event log must be empty.")
        self._assert(
            state["active_player_id"] == "player_1"
            and state["priority_player_id"] == "player_1",
            "Initial active or priority player is invalid.",
        )
        self._assert_player_zone_counts(state, "player_1", hand_count=1, deck_count=2)
        self._assert_player_zone_counts(state, "player_2", hand_count=1, deck_count=2)

    def _record_action_checkpoint(self, session, checkpoint_id, player_id):
        before = session.export_canonical_match_state()
        before_bytes = canonical_json_bytes(before)
        action_space = session.get_action_space(player_id)
        after = session.export_canonical_match_state()
        self._assert(
            before == after and before_bytes == canonical_json_bytes(after),
            "Legal action generation mutated MatchState.",
            {"checkpoint_id": checkpoint_id},
        )
        actions = action_space.get("actions") or []
        actual_order = [
            (action.get("order_rank"), action.get("action_type"), action.get("action_id"))
            for action in actions
        ]
        expected_order = sorted(actual_order)
        self._assert(
            actual_order == expected_order,
            "Runtime legal action ordering is not canonical.",
            {"checkpoint_id": checkpoint_id},
        )
        for action in actions:
            self._assert(
                action.get("order_rank") == LEGAL_ACTION_ORDER_RANKS.get(action.get("action_type")),
                "Runtime legal action order_rank is invalid.",
                {"checkpoint_id": checkpoint_id, "action_type": action.get("action_type")},
            )
        checkpoint = {
            "checkpoint_id": checkpoint_id,
            "state_version": action_space["state_version"],
            "player_id": player_id,
            "action_space": _strip_implementation_metadata(action_space),
            "canonical_action_ordering": {
                "profile": "canonical_legal_action_ordering_v1",
                "keys": ["order_rank", "action_type", "action_id"],
                "actions": [
                    {
                        "action_type": action["action_type"],
                        "action_id": action["action_id"],
                        "order_rank": action["order_rank"],
                    }
                    for action in actions
                ],
            },
            "state_unchanged": True,
            "state_sha256": sha256_bytes(before_bytes),
        }
        return checkpoint, deepcopy(action_space)

    def _select_action(self, action_space, action_type, player_id):
        matches = [
            action
            for action in action_space.get("actions", [])
            if action.get("action_type") == action_type
            and action.get("player_id") == player_id
            and action.get("enabled") is True
        ]
        if len(matches) != 1:
            raise RuntimeComparisonFixtureError(
                "ACTION_NOT_FOUND",
                self.step_id,
                "Required enabled action was not found exactly once.",
                {"action_type": action_type, "player_id": player_id},
            )
        return deepcopy(matches[0])

    def _submit(self, session, request, requests, responses):
        request_before = deepcopy(request)
        self._assert(set(request) == _REQUEST_FIELDS, "Canonical request fields are invalid.")
        self._assert(request["payload"] == {}, "Fixture request payload must be empty.")
        response = session.step(request)
        self._assert(request == request_before, "Action request input was mutated.")
        self._assert(isinstance(response.get("events"), list), "Response events must be a list.")
        self._assert(
            isinstance(response.get("diagnostics"), list),
            "Response diagnostics must be a list.",
        )
        self._assert("reason" in response, "Response reason field is missing.")
        requests.append(deepcopy(request))
        responses.append(deepcopy(response))
        return response

    def _assert_accepted_response(
        self,
        response,
        state_version_before,
        state_version_after,
        action_type,
        event_sequence,
    ):
        valid = (
            response.get("accepted") is True
            and response.get("success") is True
            and response.get("reason") is None
            and response.get("action_type") == action_type
            and response.get("state_version_before") == state_version_before
            and response.get("state_version_after") == state_version_after
            and response.get("new_event_count") == 1
            and response.get("new_event_sequences") == [event_sequence]
            and len(response.get("events") or []) == 1
            and response.get("diagnostics") == []
            and response.get("invariants_ok") is True
        )
        self._assert(valid, "Accepted action response does not match the canonical contract.")

    def _assert_stale_response(self, response):
        expected_diagnostic = {
            "code": "STALE_STATE_VERSION",
            "severity": "error",
            "category": "request_validation",
            "expected_state_version": 0,
            "current_state_version": 1,
            "retry_policy": "refresh_projection",
        }
        valid = (
            response.get("request_id") == REQUEST_IDS["stale_end_turn_player_1"]
            and response.get("accepted") is False
            and response.get("success") is False
            and response.get("reason") == "stale_state_version"
            and response.get("state_version_before") == 1
            and response.get("state_version_after") == 1
            and response.get("events") == []
            and response.get("new_event_count") == 0
            and response.get("new_event_sequences") == []
            and response.get("diagnostics") == [expected_diagnostic]
            and response.get("invariants_ok") is True
        )
        self._assert(valid, "Stale action response does not match the canonical contract.")

    def _assert_player_zone_counts(self, state, player_id, hand_count, deck_count):
        player = next(
            (item for item in state.get("players", []) if item.get("player_id") == player_id),
            None,
        )
        self._assert(player is not None, "Canonical state is missing a player.")
        self._assert(
            len(player["hand_card_instance_ids"]) == hand_count
            and len(player["deck_card_instance_ids"]) == deck_count,
            "Canonical player zone counts are invalid.",
            {"player_id": player_id},
        )

    def _assert_event_sequence(self, state, event_types, event_sequences):
        events = state.get("event_log") or []
        self._assert(
            [event.get("event_type") for event in events] == event_types
            and [event.get("event_sequence") for event in events] == event_sequences,
            "Canonical event sequence is invalid.",
        )

    def _build_immutability_result(
        self,
        before,
        after,
        hash_before,
        hash_after,
        input_request_unchanged,
    ):
        component_fields = {
            "registry": "card_instances",
            "player_zone_lists": "players",
            "topology": "domain_topologies",
            "occupancy": "domain_occupancies",
            "event_log": "event_log",
            "active_player": "active_player_id",
            "priority_player": "priority_player_id",
            "state_version": "state_version",
        }
        components = {
            name: before[field_name] == after[field_name]
            for name, field_name in component_fields.items()
        }
        self._assert(all(components.values()), "Stale rejection changed a MatchState component.")
        return {
            "canonical_state_sha256_before": hash_before,
            "canonical_state_sha256_after": hash_after,
            "canonical_state_unchanged": before == after and hash_before == hash_after,
            "input_request_unchanged": input_request_unchanged,
            "components": components,
        }

    def _capture_player_snapshot(self, session, player_id):
        state_before = session.export_canonical_match_state()
        bytes_before = canonical_json_bytes(state_before)
        snapshot = session.get_player_snapshot(player_id)
        state_after = session.export_canonical_match_state()
        self._assert(
            state_before == state_after and bytes_before == canonical_json_bytes(state_after),
            "Player-visible snapshot generation mutated MatchState.",
            {"player_id": player_id},
        )
        canonical_snapshot = _strip_implementation_metadata(snapshot)
        self._assert_snapshot_visibility(canonical_snapshot, player_id)
        visibility_result = self._assert_no_hidden_information_leak(
            canonical_snapshot,
            state_after,
            player_id,
        )
        return canonical_snapshot, visibility_result

    def _assert_snapshot_visibility(self, snapshot, player_id):
        self._assert(
            snapshot.get("snapshot_type") == "player_visible_snapshot"
            and snapshot.get("visibility_mode") == "player"
            and snapshot.get("player_id") == player_id,
            "Player-visible snapshot identity is invalid.",
        )
        players = {item["player_id"]: item for item in snapshot.get("players", [])}
        self._assert(set(players) == {"player_1", "player_2"}, "Snapshot players are invalid.")
        opponent_id = "player_2" if player_id == "player_1" else "player_1"
        own_zones = players[player_id]["zones"]
        opponent_zones = players[opponent_id]["zones"]
        valid = (
            own_zones["hand"]["visibility_mode"] == "owner_visible"
            and len(own_zones["hand"]["objects"]) == 2
            and opponent_zones["hand"]["visibility_mode"] == "count_only"
            and opponent_zones["hand"]["objects"] == []
            and all(player["zones"]["deck"]["visibility_mode"] == "count_only" for player in players.values())
            and all(player["zones"]["deck"]["objects"] == [] for player in players.values())
            and all(player["zones"]["discard"]["visibility_mode"] == "public" for player in players.values())
            and snapshot.get("board", {}).get("visibility_mode") == "public"
        )
        self._assert(valid, "Player-visible snapshot visibility policy is invalid.")

    def _assert_no_hidden_information_leak(self, snapshot, state, player_id):
        players = {item["player_id"]: item for item in state["players"]}
        registry = {item["card_instance_id"]: item for item in state["card_instances"]}
        opponent_id = "player_2" if player_id == "player_1" else "player_1"
        opponent_hand_ids = set(players[opponent_id]["hand_card_instance_ids"])
        opponent_hand_card_ids = {
            registry[card_instance_id]["card_id"] for card_instance_id in opponent_hand_ids
        }
        deck_instance_ids = {
            card_instance_id
            for player in players.values()
            for card_instance_id in player["deck_card_instance_ids"]
        }
        forbidden_values = opponent_hand_ids | opponent_hand_card_ids | deck_instance_ids
        leaked_values = forbidden_values & set(_scalar_values(snapshot))
        forbidden_keys = _FORBIDDEN_PLAYER_SNAPSHOT_KEYS & set(_nested_keys(snapshot))
        python_metadata = [
            value
            for value in _scalar_values(snapshot)
            if isinstance(value, str) and value.startswith("python.")
        ]
        passed = not leaked_values and not forbidden_keys and not python_metadata
        self._assert(
            passed,
            "Player-visible snapshot leaked hidden or implementation-specific information.",
            {
                "player_id": player_id,
                "hidden_value_leak_count": len(leaked_values),
                "forbidden_key_count": len(forbidden_keys),
                "python_metadata_count": len(python_metadata),
            },
        )
        return {
            "passed": True,
            "hidden_value_leak_count": 0,
            "forbidden_key_count": 0,
            "python_metadata_count": 0,
            "snapshot_non_mutating": True,
        }

    def _assert_result_hygiene(self, result):
        self._assert(not _contains_absolute_path(result), "Fixture result contains an absolute path.")
        self._assert(
            not any(
                isinstance(value, str) and value.startswith("python.")
                for value in _scalar_values(result)
            ),
            "Fixture result contains Python-specific metadata.",
        )

    def _assert(self, condition, message, details=None):
        if not condition:
            raise RuntimeComparisonFixtureError(
                "STEP_ASSERTION_FAILED",
                self.step_id,
                message,
                details,
            )


def _strip_implementation_metadata(value):
    if isinstance(value, dict):
        return {
            key: _strip_implementation_metadata(nested)
            for key, nested in value.items()
            if key not in _IMPLEMENTATION_METADATA_KEYS
        }
    if isinstance(value, list):
        return [_strip_implementation_metadata(item) for item in value]
    return deepcopy(value)


def _nested_keys(value):
    keys = []
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.append(key)
            keys.extend(_nested_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.extend(_nested_keys(nested))
    return keys


def _scalar_values(value):
    values = []
    if isinstance(value, dict):
        for nested in value.values():
            values.extend(_scalar_values(nested))
    elif isinstance(value, list):
        for nested in value:
            values.extend(_scalar_values(nested))
    else:
        values.append(value)
    return values


def _contains_absolute_path(value):
    for scalar in _scalar_values(value):
        if not isinstance(scalar, str):
            continue
        if Path(scalar).is_absolute():
            return True
        if len(scalar) >= 3 and scalar[0].isalpha() and scalar[1] == ":" and scalar[2] in {"/", "\\"}:
            return True
    return False


__all__ = [
    "RuntimeComparisonFixtureError",
    "run_python_reference_fixture",
]
