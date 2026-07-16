import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ENGINE_PYTHON_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = ENGINE_PYTHON_DIR / "engine"
AI_VS_AI_DIR = ENGINE_PYTHON_DIR / "tools" / "ai_vs_ai"
FIXTURE_DIR = (
    ENGINE_PYTHON_DIR.parent
    / "runtime_comparison"
    / "fixtures"
    / "minimal_draw_end_turn_v1"
)
FIXTURE_PATH = FIXTURE_DIR / "fixture.json"
RUNTIME_PACKAGE_DIR = FIXTURE_DIR / "runtime_package"
READER_PATH = AI_VS_AI_DIR / "runtime_package_reader.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
CANONICAL_PATH = ENGINE_DIR / "canonical_match_state.py"


def _load_module(module_name, path):
    for module_dir in (str(ENGINE_PYTHON_DIR), str(ENGINE_DIR), str(AI_VS_AI_DIR)):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestCanonicalMatchStateSerialization(unittest.TestCase):
    def setUp(self):
        self.canonical = _load_module("canonical_match_state", CANONICAL_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.runtime_package = self.reader.load_runtime_package(RUNTIME_PACKAGE_DIR)

    def test_initial_fixture_serializes_complete_ordered_canonical_state(self):
        session, state = self._create_session()

        dto = session.export_canonical_match_state()

        self.assertEqual(
            set(dto),
            set(self.canonical.FIELD_POLICIES["canonical_match_state"]["required_value"]),
        )
        self.assertEqual(dto["schema_version"], "aeterna-canonical-match-state-v1")
        self.assertEqual(dto["contract_type"], "canonical_match_state")
        self.assertEqual(dto["match_id"], self.fixture["match_id"])
        self.assertEqual(dto["state_version"], 0)
        self.assertEqual(dto["turn_number"], 1)
        self.assertEqual(dto["phase"], "main")
        self.assertEqual(dto["active_player_id"], "player_1")
        self.assertEqual(dto["priority_player_id"], "player_1")
        self.assertEqual(dto["priority_model"], "minimal_priority_model_v1")
        self.assertEqual(dto["semantic_metadata"], {})
        self.assertEqual(dto["event_log"], [])

        self.assertEqual([player["player_id"] for player in dto["players"]], ["player_1", "player_2"])
        for player_index, player in enumerate(dto["players"], start=1):
            prefix = "ci_player_%s_" % player_index
            self.assertEqual(player["hand_card_instance_ids"], [prefix + "0001"])
            self.assertEqual(
                player["deck_card_instance_ids"],
                [prefix + "0002", prefix + "0003"],
            )
            self.assertEqual(player["discard_card_instance_ids"], [])

        expected_instance_ids = [
            "ci_player_1_0001",
            "ci_player_2_0001",
            "ci_player_1_0002",
            "ci_player_2_0002",
            "ci_player_1_0003",
            "ci_player_2_0003",
        ]
        self.assertEqual(
            [record["card_instance_id"] for record in dto["card_instances"]],
            expected_instance_ids,
        )
        self.assertEqual(len(dto["card_instances"]), 6)
        for record in dto["card_instances"]:
            sequence = record["created_sequence"]
            expected_zone = "hand" if sequence == 1 else "deck"
            expected_index = 0 if sequence == 1 else sequence - 2
            self.assertEqual(record["zone"], expected_zone)
            self.assertEqual(record["zone_index"], expected_index)
            self.assertEqual(record["zone_sequence"], 1)
            self.assertIsNone(record["activity_state"])
            self.assertEqual(
                record["semantic_metadata"],
                {
                    "creation_reason": "initial_match_setup",
                    "initial_zone": expected_zone,
                },
            )

        self.assertEqual(
            [entry["player_id"] for entry in dto["domain_topologies"]],
            ["player_1", "player_2"],
        )
        self.assertEqual(
            [entry["player_id"] for entry in dto["domain_occupancies"]],
            ["player_1", "player_2"],
        )
        for topology_entry, occupancy_entry in zip(
            dto["domain_topologies"], dto["domain_occupancies"]
        ):
            topology = topology_entry["topology"]
            occupancy = occupancy_entry["occupancy"]
            self.assertEqual(topology["rows"], ["horizon", "zenith"])
            self.assertEqual([current["current_index"] for current in topology["currents"]], list(range(1, 7)))
            self.assertEqual(len(topology["positions"]), 18)
            self.assertEqual(len(occupancy["slots"]), 12)
            self.assertTrue(all(slot["occupancy_state"] == "empty" for slot in occupancy["slots"]))
            self.assertEqual(topology["semantic_metadata"]["topology_model"], "base_game_six_current_v0")
            self.assertEqual(occupancy["semantic_metadata"]["slot_capacity"], 1)

        self.assertFalse(_contains_exact_key(dto, {"metadata", "source", "authority"}))
        self.assertEqual(state.event_log, [])

    def test_draw_and_end_turn_preserve_ordered_typed_event_semantics(self):
        session, state = self._create_session()
        _submit_action(session, "draw_card")
        _submit_action(session, "end_turn")
        raw_events = deepcopy(state.event_log)

        first = session.export_canonical_match_state()
        second = session.export_canonical_match_state()

        self.assertEqual(first, second)
        self.assertEqual(first["state_version"], 2)
        self.assertEqual(first["active_player_id"], "player_2")
        self.assertEqual(first["priority_player_id"], "player_2")
        self.assertEqual(
            [event["event_type"] for event in first["event_log"]],
            ["zone_move", "turn_transition"],
        )
        self.assertEqual([event["event_index"] for event in first["event_log"]], [0, 1])
        self.assertEqual([event["event_sequence"] for event in first["event_log"]], [1, 2])

        for raw, canonical in zip(raw_events, first["event_log"]):
            for field_name in (
                "schema_version",
                "contract_type",
                "event_index",
                "event_sequence",
                "event_type",
                "player_id",
                "action_type",
                "turn_number",
                "state_version",
            ):
                self.assertEqual(canonical[field_name], raw[field_name])
            for field_name, value in raw["payload"].items():
                if field_name != "metadata":
                    self.assertEqual(canonical["payload"][field_name], value)
            self.assertEqual(canonical["semantic_metadata"], {})
            self.assertNotIn("metadata", canonical["payload"])
            self.assertNotIn("authority", canonical["payload"]["semantic_metadata"])

        self.assertEqual(
            first["event_log"][0]["payload"]["semantic_metadata"],
            {
                "applied": True,
                "semantic_event_type": "card_drawn",
                "zone_operation": "draw_card",
            },
        )
        self.assertEqual(
            first["event_log"][1]["payload"]["semantic_metadata"],
            {
                "applied": True,
                "semantic_event_type": "end_turn_resolved",
                "turn_model": "minimal_alternating_players",
            },
        )
        self.assertFalse(_contains_exact_key(first, {"metadata", "source", "authority"}))

    def test_serializer_and_session_boundary_are_read_only_and_detached(self):
        session, state = self._create_session()
        state_before = deepcopy(state)
        history_before = session.get_action_response_history()

        direct = self.canonical.serialize_match_state(state, self.runtime_package)
        exported = session.export_canonical_match_state()

        self.assertEqual(direct, exported)
        self.assertEqual(state, state_before)
        self.assertEqual(session.get_action_response_history(), history_before)
        self.assertEqual(state.event_log, [])
        self.assertEqual(state.state_version, 0)

        exported["players"][0]["deck_card_instance_ids"].clear()
        exported["card_instances"][0]["semantic_metadata"]["initial_zone"] = "mutated"
        exported["domain_topologies"][0]["topology"]["rows"].reverse()

        self.assertEqual(len(state.players[0].deck_card_instance_ids), 2)
        self.assertEqual(
            state.card_instances["ci_player_1_0001"]["metadata"]["initial_zone"],
            "hand",
        )
        self.assertEqual(state.domain_topologies["player_1"]["rows"], ["horizon", "zenith"])
        self.assertEqual(session.export_canonical_match_state(), direct)

    def test_invalid_state_or_unknown_metadata_fails_without_partial_dto(self):
        session, state = self._create_session()
        state.card_instances["ci_player_1_0001"]["metadata"]["future_semantic_fact"] = "x"

        with self.assertRaisesRegex(
            self.canonical.CanonicalMatchStateSerializationError,
            "unknown metadata fields: future_semantic_fact",
        ):
            session.export_canonical_match_state()

        session, state = self._create_session()
        del state.domain_occupancies["player_2"]
        with self.assertRaisesRegex(
            self.canonical.CanonicalMatchStateSerializationError,
            "MatchState invariant validation failed",
        ):
            session.export_canonical_match_state()

    def _create_session(self):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        state = session.create_match(
            deck_id_a=self.fixture["deck_ids"][0],
            deck_id_b=self.fixture["deck_ids"][1],
            match_id=self.fixture["match_id"],
            player_ids=tuple(self.fixture["player_ids"]),
            starting_hand_size=self.fixture["starting_hand_size"],
        )
        return session, state


def _submit_action(session, action_type):
    action = next(
        action
        for action in session.list_legal_actions()
        if action["action_type"] == action_type and action["enabled"] is True
    )
    response = session.step(session.build_action_request(action))
    if response["accepted"] is not True:
        raise AssertionError("Action was rejected: %s" % action_type)
    return response


def _contains_exact_key(value, keys):
    if isinstance(value, dict):
        return any(key in keys for key in value) or any(
            _contains_exact_key(nested, keys) for nested in value.values()
        )
    if isinstance(value, list):
        return any(_contains_exact_key(nested, keys) for nested in value)
    return False


if __name__ == "__main__":
    unittest.main()
