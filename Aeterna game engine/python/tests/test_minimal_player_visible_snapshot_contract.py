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
SNAPSHOT_PATH = ENGINE_DIR / "player_visible_snapshot.py"
SESSION_PATH = ENGINE_DIR / "minimal_engine_session.py"
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


class TestMinimalPlayerVisibleSnapshotContract(unittest.TestCase):
    def setUp(self):
        self.snapshot_module = _load_module("player_visible_snapshot", SNAPSHOT_PATH)
        self.session_module = _load_module("minimal_engine_session", SESSION_PATH)
        self.reader = _load_module("runtime_package_reader", READER_PATH)
        self.runtime_package = self.reader.load_runtime_package(GODOT_RUNTIME_PACKAGE_DIR)

    def test_initial_snapshot_contract_and_visibility_policy(self):
        session = self._create_session("PLAYER-SNAPSHOT-INITIAL-001")

        snapshot = session.get_player_snapshot("P1")
        self_projection = _player(snapshot, "P1")
        opponent_projection = _player(snapshot, "P2")

        self.assertEqual(snapshot["schema_version"], "engine-player-visible-snapshot-v2")
        self.assertEqual(snapshot["contract_type"], "engine_player_visible_snapshot")
        self.assertEqual(snapshot["snapshot_type"], "player_visible_snapshot")
        self.assertEqual(snapshot["visibility_mode"], "player")
        self.assertEqual(
            snapshot["visibility_policy"],
            {
                "model": "minimal_visibility_projection_v0",
                "deck": "count_only",
                "own_hand": "owner_visible",
                "opponent_hand": "count_only",
                "discard": "public",
                "board": "public",
            },
        )
        self.assertEqual(snapshot["board"]["board_model"], "minimal-public-domain-board-v0")
        self.assertEqual([player["relation"] for player in snapshot["players"]], ["self", "opponent"])
        self.assertEqual(sum(player["is_viewer"] for player in snapshot["players"]), 1)

        for projection in (self_projection, opponent_projection):
            deck = projection["zones"]["deck"]
            discard = projection["zones"]["discard"]
            self.assertEqual(deck["visibility_mode"], "count_only")
            self.assertTrue(deck["redacted"])
            self.assertEqual(deck["objects"], [])
            self.assertEqual(discard["visibility_mode"], "public")
            self.assertFalse(discard["redacted"])
            self.assertEqual(discard["objects"], [])

        self.assertEqual(self_projection["zones"]["hand"]["visibility_mode"], "owner_visible")
        self.assertFalse(self_projection["zones"]["hand"]["redacted"])
        self.assertEqual(self_projection["zones"]["hand"]["objects"], [])
        self.assertEqual(opponent_projection["zones"]["hand"]["visibility_mode"], "count_only")
        self.assertTrue(opponent_projection["zones"]["hand"]["redacted"])
        self.assertEqual(opponent_projection["zones"]["hand"]["objects"], [])
        json.dumps(snapshot, ensure_ascii=False)
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(snapshot)["valid"])

    def test_own_draw_exposes_only_owner_hand_object_reference(self):
        session = self._create_session("PLAYER-SNAPSHOT-OWN-DRAW-001")
        state = session.state
        player = state.get_player("P1")
        initial_deck_count = len(player.deck_card_instance_ids)
        drawn_instance_id = player.deck_card_instance_ids[0]
        drawn_card_id = state.get_card_id(drawn_instance_id)

        _draw(session)
        snapshot = session.get_player_snapshot("P1")
        projection = _player(snapshot, "P1")
        hand = projection["zones"]["hand"]

        self.assertEqual(projection["hand_count"], 1)
        self.assertEqual(hand["count"], 1)
        self.assertEqual(len(hand["objects"]), 1)
        reference = hand["objects"][0]
        self.assertEqual(reference["contract_type"], "object_reference")
        self.assertEqual(reference["object_type"], "card_instance")
        self.assertEqual(reference["card_instance_id"], drawn_instance_id)
        self.assertEqual(reference["card_id"], drawn_card_id)
        self.assertEqual(reference["zone"], "hand")
        self.assertEqual(projection["deck_count"], initial_deck_count - 1)
        self.assertEqual(projection["zones"]["deck"]["objects"], [])
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(snapshot)["valid"])

    def test_opponent_hand_is_count_only_without_hidden_values_or_order(self):
        session = self._create_session("PLAYER-SNAPSHOT-OPPONENT-REDACTION-001")
        state = session.state
        drawn_instance_id = state.get_player("P1").deck_card_instance_ids[0]
        drawn_card_id = state.get_card_id(drawn_instance_id)
        _draw(session)

        snapshot = session.get_player_snapshot("P2")
        opponent = _player(snapshot, "P1")
        opponent_hand = opponent["zones"]["hand"]
        serialized_hand = json.dumps(opponent_hand, ensure_ascii=False)

        self.assertEqual(opponent["relation"], "opponent")
        self.assertEqual(opponent["hand_count"], 1)
        self.assertEqual(opponent_hand["count"], 1)
        self.assertEqual(opponent_hand["visibility_mode"], "count_only")
        self.assertTrue(opponent_hand["redacted"])
        self.assertEqual(opponent_hand["objects"], [])
        self.assertFalse(opponent_hand["metadata"]["ordered"])
        self.assertNotIn(drawn_card_id, serialized_hand)
        self.assertNotIn(drawn_instance_id, serialized_hand)
        self.assertNotIn("zone_index", serialized_hand)
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(snapshot)["valid"])

    def test_reversed_view_projects_same_state_differently_without_mutation(self):
        session = self._create_session("PLAYER-SNAPSHOT-REVERSED-VIEW-001")
        state = session.state
        _draw(session)
        _end_turn(session)
        p2_drawn_instance_id = state.get_player("P2").deck_card_instance_ids[0]
        _draw(session)
        state_before = deepcopy(state)

        p2_snapshot = session.get_player_snapshot("P2")
        p1_snapshot = session.get_player_snapshot("P1")

        self.assertEqual(_player(p2_snapshot, "P2")["zones"]["hand"]["objects"][0]["card_instance_id"], p2_drawn_instance_id)
        self.assertEqual(_player(p1_snapshot, "P2")["zones"]["hand"]["objects"], [])
        self.assertEqual(_player(p1_snapshot, "P2")["zones"]["hand"]["count"], 1)
        self.assertEqual(p2_snapshot["state_version"], p1_snapshot["state_version"])
        self.assertNotEqual(p2_snapshot["players"], p1_snapshot["players"])
        self.assertEqual(state, state_before)
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(p2_snapshot)["valid"])
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(p1_snapshot)["valid"])

    def test_public_discard_is_visible_to_both_players(self):
        session = self._create_session("PLAYER-SNAPSHOT-PUBLIC-DISCARD-001")
        state = session.state
        player = state.get_player("P1")
        card_instance_id = player.deck_card_instance_ids.pop(0)
        player.discard_card_instance_ids.append(card_instance_id)
        record = state.get_card_instance(card_instance_id)
        record["zone"] = "discard"
        record["zone_index"] = 0
        record["visibility"] = "public"
        record["zone_sequence"] += 1
        for zone_index, remaining_id in enumerate(player.deck_card_instance_ids):
            state.get_card_instance(remaining_id)["zone_index"] = zone_index

        p1_snapshot = session.get_player_snapshot("P1")
        p2_snapshot = session.get_player_snapshot("P2")
        p1_discard = _player(p1_snapshot, "P1")["zones"]["discard"]
        p2_discard = _player(p2_snapshot, "P1")["zones"]["discard"]

        self.assertEqual(p1_discard["objects"], p2_discard["objects"])
        self.assertEqual(p1_discard["objects"][0]["card_instance_id"], card_instance_id)
        self.assertEqual(p1_discard["objects"][0]["visibility"], "public")
        self.assertEqual(p1_discard["count"], len(p1_discard["objects"]))
        self.assertEqual(p2_discard["count"], len(p2_discard["objects"]))
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(p1_snapshot)["valid"])
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(p2_snapshot)["valid"])

    def test_snapshot_does_not_leak_internal_state_or_hidden_event_data(self):
        session = self._create_session("PLAYER-SNAPSHOT-HIDDEN-REGRESSION-001")
        state = session.state
        p1_hidden_instance_id = state.get_player("P1").deck_card_instance_ids[0]
        p1_hidden_card_id = state.get_card_id(p1_hidden_instance_id)
        _draw(session)
        snapshot = session.get_player_snapshot("P2")
        serialized = json.dumps(snapshot, ensure_ascii=False)

        for forbidden_key in (
            "card_instances",
            "deck_card_instance_ids",
            "hand_card_instance_ids",
            "discard_card_instance_ids",
            "debug_snapshot",
            "event_log",
            "payload",
        ):
            self.assertFalse(_contains_key(snapshot, forbidden_key), forbidden_key)
        self.assertNotIn(p1_hidden_instance_id, serialized)
        self.assertNotIn(p1_hidden_card_id, serialized)
        self.assertTrue(self.snapshot_module.validate_player_visible_snapshot(snapshot)["valid"])

    def test_snapshot_and_visible_object_references_are_deep_copied(self):
        session = self._create_session("PLAYER-SNAPSHOT-DEEP-COPY-001")
        state = session.state
        _draw(session)
        card_instance_id = state.get_player("P1").hand_card_instance_ids[0]
        registry_record = state.get_card_instance(card_instance_id)
        original_record = deepcopy(registry_record)
        snapshot = session.get_player_snapshot("P1")
        reference = _player(snapshot, "P1")["zones"]["hand"]["objects"][0]

        reference["card_id"] = "MUTATED-CARD"
        reference["metadata"]["source"] = "mutated"
        self.assertEqual(registry_record, original_record)

        registry_record["metadata"]["after_snapshot"] = True
        self.assertNotIn("after_snapshot", reference["metadata"])

        snapshot["metadata"]["hidden_information_model"] = "mutated"
        snapshot["players"][0]["zones"]["hand"]["metadata"]["authority"] = "mutated"
        fresh_snapshot = session.get_player_snapshot("P1")
        self.assertEqual(fresh_snapshot["metadata"]["hidden_information_model"], "minimal_visibility_projection_v0")
        self.assertEqual(_player(fresh_snapshot, "P1")["zones"]["hand"]["metadata"]["authority"], "engine")

    def test_validator_reports_visibility_and_structure_errors_without_raising(self):
        session = self._create_session("PLAYER-SNAPSHOT-VALIDATOR-NEGATIVE-001")
        _draw(session)
        valid = session.get_player_snapshot("P1")
        self_hand = _player(valid, "P1")["zones"]["hand"]

        cases = []
        exposed_deck = deepcopy(valid)
        _player(exposed_deck, "P1")["zones"]["deck"]["objects"] = [deepcopy(self_hand["objects"][0])]
        cases.append(("HIDDEN_ZONE_OBJECTS_EXPOSED", exposed_deck))

        visible_opponent_hand = deepcopy(valid)
        opponent_hand = _player(visible_opponent_hand, "P2")["zones"]["hand"]
        opponent_hand["visibility_mode"] = "owner_visible"
        opponent_hand["redacted"] = False
        cases.append(("ZONE_VISIBILITY_INVALID", visible_opponent_hand))

        count_mismatch = deepcopy(valid)
        _player(count_mismatch, "P1")["zones"]["hand"]["count"] = 2
        cases.append(("VISIBLE_ZONE_COUNT_MISMATCH", count_mismatch))

        zone_mismatch = deepcopy(valid)
        _player(zone_mismatch, "P1")["zones"]["hand"]["objects"][0]["zone"] = "discard"
        cases.append(("OBJECT_REFERENCE_ZONE_MISMATCH", zone_mismatch))

        duplicate_visible = deepcopy(valid)
        projection = _player(duplicate_visible, "P1")
        duplicate_reference = deepcopy(projection["zones"]["hand"]["objects"][0])
        duplicate_reference["zone"] = "discard"
        projection["discard_count"] = 1
        projection["zones"]["discard"]["count"] = 1
        projection["zones"]["discard"]["objects"] = [duplicate_reference]
        cases.append(("VISIBLE_OBJECT_DUPLICATE", duplicate_visible))

        missing_self = deepcopy(valid)
        for player in missing_self["players"]:
            player["relation"] = "opponent"
            player["is_viewer"] = False
        cases.append(("PLAYER_RELATION_INVALID", missing_self))

        bad_policy = deepcopy(valid)
        bad_policy["visibility_policy"]["deck"] = "public"
        cases.append(("VISIBILITY_POLICY_INVALID", bad_policy))

        for expected_code, invalid in cases:
            with self.subTest(expected_code=expected_code):
                result = self.snapshot_module.validate_player_visible_snapshot(invalid)
                self.assertFalse(result["valid"])
                self.assertIn(expected_code, _error_codes(result))

        for invalid in (None, [], "snapshot"):
            with self.subTest(non_dict=invalid):
                result = self.snapshot_module.validate_player_visible_snapshot(invalid)
                json.dumps(result, ensure_ascii=False)
                self.assertFalse(result["valid"])
                self.assertIn("SNAPSHOT_NOT_DICT", _error_codes(result))

    def test_unknown_viewer_is_a_controlled_session_error(self):
        session = self._create_session("PLAYER-SNAPSHOT-UNKNOWN-VIEWER-001")
        state_before = deepcopy(session.state)

        with self.assertRaisesRegex(self.session_module.MinimalEngineSessionError, "Unknown player_id: PX"):
            session.get_player_snapshot("PX")

        self.assertEqual(session.state, state_before)
        self.assertEqual(session.get_action_response_history(), [])
        self.assertEqual(session.get_event_log(), [])

    def _create_session(self, match_id):
        session = self.session_module.MinimalEngineSession(self.runtime_package)
        session.create_match(match_id=match_id)
        return session


def _player(snapshot, player_id):
    return next(player for player in snapshot["players"] if player["player_id"] == player_id)


def _action(session, action_type):
    return next(action for action in session.get_action_space()["actions"] if action["action_type"] == action_type)


def _draw(session):
    return session.step(session.build_action_request(_action(session, "draw_card")))


def _end_turn(session):
    return session.step(session.build_action_request(_action(session, "end_turn")))


def _contains_key(value, key):
    if isinstance(value, dict):
        return key in value or any(_contains_key(nested, key) for nested in value.values())
    if isinstance(value, list):
        return any(_contains_key(nested, key) for nested in value)
    return False


def _error_codes(result):
    return {error.get("code") for error in result.get("errors", [])}


if __name__ == "__main__":
    unittest.main()
