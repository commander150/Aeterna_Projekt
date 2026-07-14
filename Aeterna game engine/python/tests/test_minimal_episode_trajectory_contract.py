import importlib
import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ENGINE_PYTHON_DIR.parents[1]
GODOT_RUNTIME_PACKAGE_DIR = PROJECT_DIR / "Aeterna game engine" / "Godot" / "runtime_package"
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
TRAJECTORY_PATH = ENGINE_DIR / "episode_trajectory.py"
ENVIRONMENT_PATH = ENGINE_DIR / "minimal_engine_environment.py"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_PYTHON_DIR), str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestMinimalEpisodeTrajectoryContract(unittest.TestCase):
    def setUp(self):
        self.trajectory = _load_module("episode_trajectory", TRAJECTORY_PATH)
        self.environment_module = _load_module("minimal_engine_environment", ENVIRONMENT_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_step_helper_creates_complete_json_contract_with_deep_copies(self):
        inputs = _step_inputs()
        originals = deepcopy(inputs)

        record = self.trajectory.create_episode_step_record(**inputs)
        roundtrip = json.loads(json.dumps(record, ensure_ascii=False))

        self.assertEqual(
            set(record),
            {
                "schema_version",
                "contract_type",
                "step_index",
                "acting_player_id",
                "observation_before",
                "selected_action",
                "action_request",
                "action_response",
                "new_events",
                "observation_after",
                "state_version_before",
                "state_version_after",
                "new_event_sequences",
                "accepted",
                "success",
                "reason",
                "selected_action_type",
                "selected_action_id",
                "metadata",
            },
        )
        self.assertEqual(record["schema_version"], "minimal-episode-step-v0")
        self.assertEqual(record["contract_type"], "minimal_episode_step")
        self.assertEqual(record["selected_action_type"], "draw_card")
        self.assertEqual(record["selected_action_id"], "draw_card:1:0:P1")
        self.assertEqual(record["new_events"], record["action_response"]["events"])
        self.assertIsNot(record["new_events"], record["action_response"]["events"])
        self.assertEqual(roundtrip, record)
        self.assertTrue(self.trajectory.validate_episode_step_record(record)["valid"])

        record["observation_before"]["action_space"]["actions"][0]["metadata"]["labels"].append("changed")
        record["selected_action"]["metadata"]["labels"].append("changed")
        record["action_request"]["payload"]["targets"].append("P2")
        record["action_response"]["events"][0]["payload"]["metadata"]["labels"].append("changed")
        record["new_events"][0]["payload"]["metadata"]["labels"].append("new-event-only")
        record["observation_after"]["player_snapshot"]["players"][0]["hand_count"] = 99
        record["metadata"]["details"]["labels"].append("changed")

        self.assertEqual(inputs, originals)
        self.assertNotEqual(
            record["new_events"][0]["payload"],
            record["action_response"]["events"][0]["payload"],
        )

    def test_step_validator_reports_structural_and_cross_field_errors(self):
        valid = self.trajectory.create_episode_step_record(**_step_inputs())
        cases = (
            ("FIELD_MISSING", _remove_metadata),
            ("STEP_INDEX_INVALID", _set_negative_step_index),
            ("STEP_INDEX_INVALID", _set_bool_step_index),
            ("OBSERVATION_STATE_VERSION_MISMATCH", _mismatch_observation_before_version),
            ("REQUEST_STATE_VERSION_MISMATCH", _mismatch_request_version),
            ("RESPONSE_STATE_VERSION_MISMATCH", _mismatch_response_version),
            ("ACTION_REQUEST_MISMATCH", _mismatch_action_request),
            ("RESPONSE_SUMMARY_MISMATCH", _mismatch_response_summary),
            ("NEW_EVENTS_MISMATCH", _mismatch_event_sequences),
            ("STEP_RECORD_INVALID", _set_replay_ready),
        )
        for expected_code, mutate in cases:
            with self.subTest(expected_code=expected_code, mutation=mutate.__name__):
                invalid = deepcopy(valid)
                mutate(invalid)

                result = self.trajectory.validate_episode_step_record(invalid)

                self.assertFalse(result["valid"])
                self.assertIn(expected_code, _error_codes(result))

        for invalid in (None, [], "step"):
            with self.subTest(non_dict=invalid):
                result = self.trajectory.validate_episode_step_record(invalid)

                json.dumps(result, ensure_ascii=False)
                self.assertFalse(result["valid"])
                self.assertIn("STEP_RECORD_INVALID", _error_codes(result))

    def test_trajectory_validator_checks_step_state_and_event_continuity(self):
        first = _trajectory_step(self.trajectory, step_index=0, before=0, after=1, event_sequence=1)
        second = _trajectory_step(self.trajectory, step_index=1, before=1, after=2, event_sequence=2)

        valid = self.trajectory.validate_episode_trajectory([first, second])

        self.assertTrue(valid["valid"])
        self.assertEqual(valid["errors"], [])
        self.assertTrue(self.trajectory.validate_episode_trajectory([])["valid"])
        self.assertIn(
            "TRAJECTORY_NOT_LIST",
            _error_codes(self.trajectory.validate_episode_trajectory(None)),
        )

        missing_index = deepcopy(first)
        missing_index.pop("step_index")
        self.assertIn(
            "STEP_INDEX_INVALID",
            _error_codes(self.trajectory.validate_episode_trajectory([missing_index])),
        )

        index_gap = deepcopy(second)
        index_gap["step_index"] = 2
        self.assertIn(
            "STEP_INDEX_SEQUENCE_INVALID",
            _error_codes(self.trajectory.validate_episode_trajectory([first, index_gap])),
        )

        discontinuous_state = _trajectory_step(
            self.trajectory,
            step_index=1,
            before=2,
            after=3,
            event_sequence=2,
        )
        self.assertIn(
            "STATE_VERSION_CONTINUITY_INVALID",
            _error_codes(self.trajectory.validate_episode_trajectory([first, discontinuous_state])),
        )

        repeated_event = _trajectory_step(
            self.trajectory,
            step_index=1,
            before=1,
            after=2,
            event_sequence=1,
        )
        self.assertIn(
            "EVENT_SEQUENCE_CONTINUITY_INVALID",
            _error_codes(self.trajectory.validate_episode_trajectory([first, repeated_event])),
        )

    def test_environment_emits_canonical_draw_trajectory_and_deterministic_json(self):
        first_environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)
        second_environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)

        first = first_environment.run_episode(max_steps=4, match_id="EPISODE-TRAJECTORY-DRAW-001")
        second = second_environment.run_episode(max_steps=4, match_id="EPISODE-TRAJECTORY-DRAW-001")

        first_json = json.dumps(first, ensure_ascii=False, sort_keys=True)
        second_json = json.dumps(second, ensure_ascii=False, sort_keys=True)
        self.assertEqual(first_json, second_json)
        self.assertEqual(first["schema_version"], "minimal-ai-vs-ai-episode-v1")
        self.assertEqual(first["contract_type"], "minimal_ai_vs_ai_episode")
        self.assertTrue(first["trajectory_validation"]["valid"])
        self.assertEqual(first["trajectory_validation"]["errors"], [])
        self.assertEqual(first["metadata"]["trajectory_model"], "full_transition_v0")
        self.assertEqual(first["metadata"]["replay_support"], "not_implemented")
        self.assertFalse(first["metadata"]["replay_ready"])
        self.assertEqual(first["steps_run"], 4)

        previous_after = None
        previous_event_sequence = None
        for step_index, step in enumerate(first["trajectory"]):
            with self.subTest(step_index=step_index):
                self.assertEqual(step["contract_type"], "minimal_episode_step")
                self.assertEqual(step["step_index"], step_index)
                self.assertIn(step["selected_action"], step["observation_before"]["action_space"]["actions"])
                self.assertEqual(step["selected_action_type"], step["selected_action"]["action_type"])
                self.assertEqual(step["selected_action_id"], step["selected_action"]["action_id"])
                self.assertEqual(step["action_request"]["action_id"], step["selected_action"]["action_id"])
                self.assertEqual(
                    step["action_request"]["expected_state_version"],
                    step["state_version_before"],
                )
                self.assertEqual(step["new_events"], step["action_response"]["events"])
                self.assertEqual(step["new_event_sequences"], step["action_response"]["new_event_sequences"])
                self.assertEqual(step["new_events"][0]["event_type"], "zone_move")
                self.assertEqual(step["observation_before"]["player_id"], step["acting_player_id"])
                self.assertEqual(
                    step["observation_after"]["player_id"],
                    step["observation_after"]["active_player_id"],
                )
                self.assertTrue(self.trajectory.validate_episode_step_record(step)["valid"])
                if previous_after is not None:
                    self.assertEqual(step["state_version_before"], previous_after)
                if previous_event_sequence is not None:
                    self.assertGreater(step["new_event_sequences"][0], previous_event_sequence)
                previous_after = step["state_version_after"]
                previous_event_sequence = step["new_event_sequences"][-1]

        self.assertEqual(first["final_observation"]["state_version"], previous_after)
        self.assertEqual(first["diagnostics_summary"]["count"], 0)
        self.assertEqual(first["transition_summary"]["rejected_response_count"], 0)

        session_events = first_environment.session.get_event_log()
        first["trajectory"][0]["new_events"][0]["payload"]["metadata"]["applied"] = False
        first["trajectory"][0]["action_response"]["events"][0]["payload"]["metadata"]["applied"] = False
        self.assertEqual(first_environment.session.get_event_log(), session_events)

    def test_environment_preserves_typed_turn_transition_events(self):
        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)
        policies = {
            "P1": _ActionTypePolicy("end_turn"),
            "P2": _ActionTypePolicy("end_turn"),
        }

        episode = environment.run_episode(
            agents=policies,
            max_steps=2,
            match_id="EPISODE-TRAJECTORY-END-TURN-001",
        )

        self.assertTrue(episode["trajectory_validation"]["valid"])
        self.assertEqual(
            [step["new_events"][0]["event_type"] for step in episode["trajectory"]],
            ["turn_transition", "turn_transition"],
        )
        self.assertEqual(
            [step["observation_after"]["player_id"] for step in episode["trajectory"]],
            ["P2", "P1"],
        )
        self.assertEqual(
            [step["new_events"][0]["event_sequence"] for step in episode["trajectory"]],
            [1, 2],
        )
        self.assertEqual(episode["diagnostics_summary"]["count"], 0)

    def test_rejected_step_remains_a_valid_complete_transition_record(self):
        empty_package = deepcopy(self.runtime_package)
        for deck in empty_package.decks_by_id.values():
            deck["card_entries"] = []
        environment = self.environment_module.MinimalEngineEnvironment(empty_package)
        policies = {"P1": _ActionTypePolicy("draw_card", require_enabled=False)}

        episode = environment.run_episode(
            agents=policies,
            max_steps=3,
            match_id="EPISODE-TRAJECTORY-REJECTED-001",
        )

        self.assertEqual(episode["steps_run"], 1)
        self.assertEqual(episode["stop_reason"], "deck_empty")
        self.assertTrue(episode["trajectory_validation"]["valid"])
        step = episode["trajectory"][0]
        self.assertIn(step["selected_action"], step["observation_before"]["action_space"]["actions"])
        self.assertFalse(step["selected_action"]["enabled"])
        self.assertFalse(step["accepted"])
        self.assertFalse(step["success"])
        self.assertEqual(step["reason"], "deck_empty")
        self.assertEqual(step["new_events"], [])
        self.assertEqual(step["new_event_sequences"], [])
        self.assertEqual(step["state_version_before"], step["state_version_after"])
        self.assertEqual(step["action_response"]["events"], [])
        self.assertTrue(self.trajectory.validate_episode_step_record(step)["valid"])

    def test_trajectory_observations_remain_player_visible_and_do_not_leak_registry(self):
        environment = self.environment_module.MinimalEngineEnvironment(self.runtime_package)

        episode = environment.run_episode(max_steps=2, match_id="EPISODE-TRAJECTORY-VISIBILITY-001")

        for step in episode["trajectory"]:
            for field_name in ("observation_before", "observation_after"):
                observation = step[field_name]
                self.assertEqual(observation["contract_type"], "minimal_engine_observation")
                self.assertIn("action_space", observation)
                self.assertIn("enabled_action_count", observation["action_space"])
                self.assertIn("disabled_action_count", observation["action_space"])
                self.assertEqual(observation["player_snapshot"]["snapshot_type"], "player_visible_snapshot")
                self.assertEqual(observation["player_snapshot"]["visibility_mode"], "player")
                self.assertEqual(len(observation["player_snapshot"]["players"]), 2)
                for player in observation["player_snapshot"]["players"]:
                    self.assertIn("deck_count", player)
                    self.assertIn("hand_count", player)
                    self.assertIn("discard_count", player)
                self.assertFalse(_contains_key(observation, "card_instances"))
                self.assertFalse(_contains_key(observation, "deck_card_instance_ids"))
                self.assertFalse(_contains_key(observation, "debug_snapshot"))
                self.assertFalse(_contains_key(observation, "deck_id"))

    def test_helper_imports_from_engine_namespace(self):
        imported = importlib.import_module("engine.episode_trajectory")

        self.assertTrue(callable(imported.create_episode_step_record))
        self.assertTrue(callable(imported.validate_episode_step_record))
        self.assertTrue(callable(imported.validate_episode_trajectory))


class _ActionTypePolicy:
    def __init__(self, action_type, require_enabled=True):
        self.action_type = action_type
        self.require_enabled = require_enabled

    def choose_action(self, observation):
        return next(
            deepcopy(action)
            for action in observation["action_space"]["actions"]
            if action["action_type"] == self.action_type
            and (not self.require_enabled or action["enabled"] is True)
        )


def _step_inputs(step_index=0, before=0, after=1, event_sequence=1, acting_player_id="P1"):
    action_id = "draw_card:1:%s:%s" % (before, acting_player_id)
    event = {
        "schema_version": "minimal-engine-event-v0",
        "contract_type": "engine_event",
        "event_index": event_sequence - 1,
        "event_sequence": event_sequence,
        "event_type": "zone_move",
        "player_id": acting_player_id,
        "action_type": "draw_card",
        "turn_number": 1,
        "state_version": after,
        "payload": {
            "event_type": "zone_move",
            "event_sequence": event_sequence,
            "metadata": {"labels": ["draw"]},
        },
    }
    selected_action = {
        "action_id": action_id,
        "action_type": "draw_card",
        "player_id": acting_player_id,
        "enabled": True,
        "request_template": {
            "expected_state_version": before,
            "payload": {},
        },
        "metadata": {"labels": ["legal"]},
    }
    action_request = {
        "request_id": "request:TEST:%s" % action_id,
        "match_id": "EPISODE-STEP-TEST-001",
        "player_id": acting_player_id,
        "action_id": action_id,
        "action_type": "draw_card",
        "expected_state_version": before,
        "payload": {"targets": []},
    }
    action_response = {
        "schema_version": "minimal-action-response-v0",
        "contract_type": "action_response",
        "response_type": "minimal_action_response",
        "request_id": action_request["request_id"],
        "player_id": acting_player_id,
        "action_id": action_id,
        "action_type": "draw_card",
        "accepted": True,
        "success": True,
        "reason": None,
        "state_version_before": before,
        "state_version_after": after,
        "new_event_count": 1,
        "new_event_sequences": [event_sequence],
        "events": [event],
    }
    return {
        "step_index": step_index,
        "acting_player_id": acting_player_id,
        "observation_before": _observation(before, acting_player_id, selected_action),
        "selected_action": selected_action,
        "action_request": action_request,
        "action_response": action_response,
        "observation_after": _observation(after, acting_player_id, selected_action),
        "metadata": {
            "source": "python.engine.minimal_engine_environment",
            "trajectory_model": "full_transition_v0",
            "replay_ready": False,
            "rules_scope": "minimal_draw_end_turn_smoke",
            "details": {"labels": ["trajectory"]},
        },
    }


def _observation(state_version, player_id, selected_action):
    return {
        "schema_version": "minimal-engine-observation-v0",
        "contract_type": "minimal_engine_observation",
        "match_id": "EPISODE-STEP-TEST-001",
        "player_id": player_id,
        "state_version": state_version,
        "active_player_id": player_id,
        "player_snapshot": {
            "snapshot_type": "player_visible_snapshot",
            "players": [
                {"player_id": "P1", "deck_count": 39, "hand_count": 1, "discard_count": 0},
                {"player_id": "P2", "deck_count": 40, "hand_count": 0, "discard_count": 0},
            ],
        },
        "action_space": {
            "actions": [deepcopy(selected_action)],
            "enabled_action_count": 1,
            "disabled_action_count": 0,
        },
    }


def _trajectory_step(trajectory, step_index, before, after, event_sequence):
    return trajectory.create_episode_step_record(
        **_step_inputs(
            step_index=step_index,
            before=before,
            after=after,
            event_sequence=event_sequence,
        )
    )


def _error_codes(result):
    return {error["code"] for error in result["errors"]}


def _contains_key(value, target_key):
    if isinstance(value, dict):
        return target_key in value or any(_contains_key(item, target_key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, target_key) for item in value)
    return False


def _remove_metadata(record):
    record.pop("metadata")


def _set_negative_step_index(record):
    record["step_index"] = -1


def _set_bool_step_index(record):
    record["step_index"] = True


def _mismatch_observation_before_version(record):
    record["observation_before"]["state_version"] += 1


def _mismatch_request_version(record):
    record["action_request"]["expected_state_version"] += 1


def _mismatch_response_version(record):
    record["action_response"]["state_version_after"] += 1


def _mismatch_action_request(record):
    record["action_request"]["action_id"] = "different-action"


def _mismatch_response_summary(record):
    record["action_response"]["accepted"] = False


def _mismatch_event_sequences(record):
    record["new_event_sequences"] = [99]


def _set_replay_ready(record):
    record["metadata"]["replay_ready"] = True


if __name__ == "__main__":
    unittest.main()
